# -*- coding: UTF-8 -*-
"""أصناف مساعدة لتغليف معلومات الآلات والأصوات."""

from collections import namedtuple

VoiceBinding = namedtuple("VoiceBinding", ["engine", "voice"])


def parse_binding(raw):
    """يحلّ سلسلة ربط من الإعدادات إلى VoiceBinding.
    الصيغة: "engineName|voiceId" أو "engineName"
    """
    if not raw or not isinstance(raw, str):
        return None
    raw = raw.strip()
    if not raw:
        return None
    for sep in ("|", "،", ",", " - "):
        if sep in raw:
            engine, _, voice = raw.partition(sep)
            engine = engine.strip()
            voice = voice.strip()
            if engine:
                return VoiceBinding(engine, voice)
    return VoiceBinding(raw, "")
