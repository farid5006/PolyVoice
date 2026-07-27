# -*- coding: UTF-8 -*-
"""PolyVoice SynthDriver — الواجهة الرئيسية نحو NVDA 2026.

كما طلب المستخدم، تمت إزالة جميع الإعدادات القياسية (السرعة، النبرة، مستوى الصوت)
لأن هذه الإضافة هي موزع (Router) بحت يعتمد على الإعدادات التي ضبطها المستخدم مسبقاً لكل آلة.
إعدادات اللغات والآلات موجودة في قسم PolyVoice الخاص في إعدادات NVDA.
"""

import config
from collections import OrderedDict
from logHandler import log

from synthDriverHandler import SynthDriver as _SynthBase
from synthDriverHandler import VoiceInfo, synthIndexReached, synthDoneSpeaking
from speech.commands import (
    IndexCommand,
    CharacterModeCommand,
    LangChangeCommand,
    BreakCommand,
)

from .languageDetection import split_sequence
from .voiceManager import VoiceManager


class SynthDriver(_SynthBase):
    """آلة النطق الموزعة PolyVoice (موزع خالص متوافق 100% مع NVDA 2026)."""

    name = "PolyVoice"
    description = "PolyVoice - موزع تلقائي بين آلات النطق"

    # تفريغ الإعدادات لأن الإضافة لا تتحكم بالصوت مباشرة (نزولاً عند رغبة المستخدم)
    supportedSettings = ()

    supportedCommands = {
        IndexCommand,
        CharacterModeCommand,
        LangChangeCommand,
        BreakCommand,
    }
    supportedNotifications = {synthIndexReached, synthDoneSpeaking}

    @classmethod
    def check(cls):
        return True

    def __init__(self):
        try:
            super().__init__()
            try:
                self._enableAutoSwitch = config.conf["PolyVoice"]["enableAutoSwitch"]
                self._defaultLang = config.conf["PolyVoice"]["defaultLang"]
            except Exception:
                self._enableAutoSwitch = True
                self._defaultLang = "ar"

            self._voiceManager = VoiceManager()
            
            import queue
            import threading
            self._speechQueue = queue.Queue()
            self._activeSynth = None
            self._doneSpeakingEvent = threading.Event()
            self._doneSpeakingEvent.set()
            
            self._speechIdCounter = 0
            self._indexReachedForCurrentSpeech = True
            self._isPumpScheduled = False

            synthDoneSpeaking.register(self._onSynthDoneSpeaking)
            synthIndexReached.register(self._onSynthIndexReached)

            log.info("PolyVoice: تهيّأت بنجاح كموزّع بين الآلات")
        except Exception:
            log.exception("PolyVoice: فشل في تهيئة SynthDriver")
            raise

    def languageIsSupported(self, lang):
        return True

    def _onSynthDoneSpeaking(self, synth):
        if synth is not self:
            if synth is not getattr(self, "_activeSynth", None):
                return
                
            if not getattr(self, "_indexReachedForCurrentSpeech", True):
                # تم إلغاء نطق سابق، وهذا الإشعار قديم وتصادم مع النطق الجديد
                return
                
            if not self._doneSpeakingEvent.is_set():
                self._doneSpeakingEvent.set()
                synthDoneSpeaking.notify(synth=self)
                return
            if not getattr(self, "_isPumpScheduled", False):
                self._isPumpScheduled = True
                self._safeCallAfter(self._pumpSpeech)

    def _onSynthIndexReached(self, synth, index):
        if synth is not self:
            if index == getattr(self, "_speechIdCounter", -1):
                self._indexReachedForCurrentSpeech = True
            synthIndexReached.notify(synth=self, index=index)

    def _safeCallAfter(self, func):
        import wx
        if wx.GetApp() is None:
            func()
        else:
            wx.CallAfter(func)

    def _safeCallLater(self, delay, func):
        import wx
        if wx.GetApp() is None:
            import time
            if delay > 0:
                time.sleep(delay / 1000.0)
            func()
        else:
            wx.CallLater(delay, func)

    def _pumpSpeech(self):
        self._isPumpScheduled = False
        if not hasattr(self, "_speechQueue"):
            return
            
        try:
            import queue
            seg = self._speechQueue.get_nowait()
        except queue.Empty:
            synthDoneSpeaking.notify(synth=self)
            self._activeSynth = None
            return

        next_instance = self._voiceManager.get_voice_instance(seg.lang)
        if not next_instance:
            if not getattr(self, "_isPumpScheduled", False):
                self._isPumpScheduled = True
                self._safeCallAfter(self._pumpSpeech)
            return

        delay = 0
        if self._activeSynth and self._activeSynth is not next_instance:
            try:
                delay = int(config.conf["PolyVoice"].get("switchDelay", 50))
            except Exception:
                delay = 50

        self._activeSynth = next_instance
        
        def execute():
            # إذا تم إلغاء النطق أثناء فترة التأخير، يجب ألا نستمر
            if self._activeSynth is not next_instance:
                return
                
            try:
                # ضبط المتغيرات *قبل* الإلغاء حتى يتم تجاهل إشعار الانتهاء الوهمي الناتج عن الإلغاء
                self._speechIdCounter += 1
                self._indexReachedForCurrentSpeech = False
                
                next_instance.cancel()
                
                # استخدام IndexCommand فريد لتفادي إشعارات الانتهاء القديمة عند الحركة السريعة
                seg.items.insert(0, IndexCommand(self._speechIdCounter))
                
                next_instance.speak(seg.items)
            except Exception:
                log.exception("PolyVoice: خطأ أثناء نطق المقطع")
                self._indexReachedForCurrentSpeech = True
                if not getattr(self, "_isPumpScheduled", False):
                    self._isPumpScheduled = True
                    self._safeCallAfter(self._pumpSpeech)

        if delay > 0:
            self._safeCallLater(delay, execute)
        else:
            execute()

    # --- النطق ---
    def speak(self, speechSequence):
        if not speechSequence:
            return

        if getattr(self, "_enableAutoSwitch", True):
            segments = split_sequence(speechSequence, default_lang=self._defaultLang)
        else:
            segments = [_SimpleSegment(speechSequence, self._defaultLang)]

        for seg in segments:
            self._speechQueue.put(seg)
            
        if self._activeSynth is None and not getattr(self, "_isPumpScheduled", False):
            self._isPumpScheduled = True
            self._safeCallAfter(self._pumpSpeech)

    def cancel(self):
        import queue
        if hasattr(self, "_speechQueue"):
            while True:
                try:
                    self._speechQueue.get_nowait()
                except queue.Empty:
                    break
        for instance in list(self._voiceManager._instanceCache.values()):
            try:
                instance.cancel()
            except Exception:
                pass
        self._activeSynth = None

    def pause(self, switch):
        for instance in list(self._voiceManager._instanceCache.values()):
            try:
                instance.pause(switch)
            except Exception:
                pass

    def terminate(self):
        try:
            synthDoneSpeaking.unregister(self._onSynthDoneSpeaking)
            synthIndexReached.unregister(self._onSynthIndexReached)
        except Exception:
            pass

        try:
            self._voiceManager.terminateAll()
        except Exception:
            log.exception("PolyVoice: استثناء أثناء إنهاء PolyVoice")
        super().terminate()
        log.info("PolyVoice: أُنهي")

    # يمكن إخفاء قائمة الأصوات أيضاً لكن نترك صوتاً وهمياً لمنع انهيار NVDA
    def _get_voice(self):
        return "PolyVoice"

    def _set_voice(self, value):
        pass

    def _getAvailableVoices(self):
        voices = OrderedDict()
        voices["PolyVoice"] = VoiceInfo("PolyVoice", "PolyVoice - موزع تلقائي", None)
        return voices


class _SimpleSegment(object):
    __slots__ = ("items", "lang")

    def __init__(self, sequence, lang):
        self.items = list(sequence)
        self.lang = lang
