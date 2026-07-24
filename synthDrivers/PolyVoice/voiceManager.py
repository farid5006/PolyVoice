# -*- coding: UTF-8 -*-
"""طبقة مدير الآلات — PolyVoice: اكتشاف صوت ليلى صراحةً من dual_sapi5 / AcaTTS."""

import synthDriverHandler
import config
from logHandler import log

from .voiceInfo import VoiceBinding, parse_binding

_EXCLUDED_ENGINES = frozenset({"polyvoice"})


class VoiceManager(object):
    """يكتشف جميع الآلات المثبتة ويوجّه اللغات بإعداداتها الأصلية الصريحة."""

    def __init__(self):
        self._instanceCache = {}
        self._availableEngines = []
        self._bindings = {}
        self._discoverInstalledEngines()
        self._loadBindingsFromConfig()

    def _discoverInstalledEngines(self):
        self._availableEngines = []
        try:
            synthList = synthDriverHandler.getSynthList()
            log.info("PolyVoice: بدء اكتشاف الآلات المثبتة...")
            for name, description in synthList:
                if name.lower() in _EXCLUDED_ENGINES:
                    continue
                self._availableEngines.append((name, description or name))
                log.info("PolyVoice: اكتشف آلة مثبتة: %s (%s)" % (name, description))
        except Exception as e:
            log.error("PolyVoice: فشل استدعاء getSynthList(): %s" % e)

        if not self._availableEngines:
            self._availableEngines.append(("sapi5", "Microsoft Speech API 5"))

    def getAvailableEngines(self):
        return list(self._availableEngines)

    def getEngineNames(self):
        return [name for name, _ in self._availableEngines]

    def findEngineName(self, target):
        if not target:
            return None
        target_lower = str(target).lower()
        for name, _ in self._availableEngines:
            if name.lower() == target_lower:
                return name
        return None

    def _loadBindingsFromConfig(self):
        self._bindings = {}
        try:
            rawBindings = config.conf["PolyVoice"]["bindings"]
            for lang, raw in rawBindings.items():
                binding = parse_binding(raw)
                if binding is not None:
                    self._bindings[lang] = binding
        except Exception:
            log.debug("PolyVoice: لا توجد روابط مخصصة بعد")

    def reloadBindings(self):
        self._loadBindingsFromConfig()
        self.terminateAll()

    def getBindingFor(self, lang):
        return self._bindings.get(lang)

    def _resolveBinding(self, lang):
        """يحدد الآلة والصوت المناسبين لأي لغة معطاة."""
        # 1. ربط صريح محدد من قبل المستخدم في شاشة الإعدادات
        binding = self.getBindingFor(lang)
        if binding:
            matched = self.findEngineName(binding.engine)
            if matched:
                return VoiceBinding(matched, binding.voice)

        # 2. افتراضي ذكي صريح للغة العربية
        if lang == "ar":
            for name, _ in self._availableEngines:
                n = name.lower()
                if ("sapi5" in n or "dual_sapi" in n) and "sapi4" not in n and "onecore" not in n:
                    return VoiceBinding(name, "")

        # 3. افتراضي ذكي صريح للغة الإنجليزية
        elif lang == "en":
            for cand in ("ibmeci", "ibmtts", "espeak", "onecore"):
                matched = self.findEngineName(cand)
                if matched:
                    return VoiceBinding(matched, "")

        # 4. افتراضي احتياطي
        for name, _ in self._availableEngines:
            n = name.lower()
            if "sapi5" in n:
                return VoiceBinding(name, "")

        if self._availableEngines:
            return VoiceBinding(self._availableEngines[0][0], "")

        return None

    def _find_engine_config(self, engine_name):
        """يبحث عن إعدادات آلة محددة (ibmeci مثلاً) من nvda.ini."""
        speech_conf = config.conf["speech"]
        sec = speech_conf.get(engine_name, {})
        if sec:
            v = sec.get("voice", "")
            r = sec.get("rate", None)
            p = sec.get("pitch", None)
            vol = sec.get("volume", None)
            return v, r, p, vol
        return None, None, None, None

    def _create_instance(self, binding, lang="ar"):
        try:
            synthCls = synthDriverHandler._getSynthDriver(binding.engine)
            instance = synthCls()

            target_voice = binding.voice
            target_rate = None
            target_pitch = None
            target_volume = None

            if not target_voice:
                # يجب جلب الإعدادات الخاصة بالآلة المختارة تحديداً، ولا يجوز خلط الإعدادات
                target_voice, target_rate, target_pitch, target_volume = self._find_engine_config(binding.engine)

            if target_voice and hasattr(instance, "voice"):
                try:
                    instance.voice = target_voice
                    log.info("PolyVoice: [%s] تم إسناد الصوت: %s" % (lang, target_voice))
                except Exception:
                    log.exception("PolyVoice: فشل إسناد الصوت %s" % target_voice)

            if target_rate is not None and hasattr(instance, "rate"):
                try:
                    instance.rate = int(target_rate)
                    log.info("PolyVoice: [%s] تم إسناد السرعة: %s" % (lang, target_rate))
                except Exception:
                    pass

            if target_pitch is not None and hasattr(instance, "pitch"):
                try:
                    instance.pitch = int(target_pitch)
                except Exception:
                    pass

            if target_volume is not None and hasattr(instance, "volume"):
                try:
                    instance.volume = int(target_volume)
                except Exception:
                    pass

            log.info("PolyVoice: تم إنشاء نسخة للآلة %s للغة %s" % (binding.engine, lang))
            return instance
        except Exception as e:
            log.exception("PolyVoice: فشل إنشاء نسخة للآلة %r" % binding.engine)
            return None

    def get_voice_instance(self, lang):
        try:
            binding = self._resolveBinding(lang)
            if binding is None:
                log.error("PolyVoice: لا توجد آلة متوفرة للغة %r" % lang)
                return None

            key = (binding.engine, binding.voice, lang)
            instance = self._instanceCache.get(key)
            if instance is None:
                instance = self._create_instance(binding, lang=lang)
                if instance is not None:
                    self._instanceCache[key] = instance
            return instance
        except Exception:
            log.exception("PolyVoice: فشل في إنشاء نسخة للغة %r" % lang)
            return None

    def terminateAll(self):
        for instance in list(self._instanceCache.values()):
            try:
                instance.cancel()
            except Exception:
                pass
            try:
                instance.terminate()
            except Exception:
                pass
        self._instanceCache.clear()

    def cancelAll(self):
        for instance in self._instanceCache.values():
            try:
                instance.cancel()
            except Exception:
                pass
