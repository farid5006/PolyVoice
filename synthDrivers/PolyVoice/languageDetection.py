# -*- coding: UTF-8 -*-
"""طبقة كشف اللغة وتقسيم تسلسل النطق لجميع لغات العالم."""

_ARABIC_RANGES = (
    (0x0600, 0x06FF),
    (0x0750, 0x077F),
    (0xFB50, 0xFDFF),
    (0xFE70, 0xFEFF),
)

_CYRILLIC_RANGES = (
    (0x0400, 0x04FF),
    (0x0500, 0x052F),
)

_HEBREW_RANGES = (
    (0x0590, 0x05FF),
)

_GREEK_RANGES = (
    (0x0370, 0x03FF),
)

_CJK_RANGES = (
    (0x4E00, 0x9FFF),
    (0x3040, 0x309F),  # Hiragana
    (0x30A0, 0x30FF),  # Katakana
    (0xAC00, 0xD7AF),  # Hangul
)


def is_arabic_char(ch):
    cp = ord(ch)
    for lo, hi in _ARABIC_RANGES:
        if lo <= cp <= hi:
            return True
    return False


def detect_lang(text, default_latin="en"):
    """يحدد رمز اللغة للنص بناءً على نطاقات يونيكود العالمية."""
    if not text:
        return default_latin

    for ch in text:
        cp = ord(ch)

        # 1. العربية
        for lo, hi in _ARABIC_RANGES:
            if lo <= cp <= hi:
                return "ar"

        # 2. السلافية / الروسية
        for lo, hi in _CYRILLIC_RANGES:
            if lo <= cp <= hi:
                return "ru"

        # 3. العبرية
        for lo, hi in _HEBREW_RANGES:
            if lo <= cp <= hi:
                return "he"

        # 4. اليونانية
        for lo, hi in _GREEK_RANGES:
            if lo <= cp <= hi:
                return "el"

        # 5. شرق آسيا (الصينية/اليابانية/الكورية)
        for lo, hi in _CJK_RANGES:
            if lo <= cp <= hi:
                return "zh"

    # النصوص اللاتينية والأرقام تعود باللغة اللاتينية الافتراضية (مثل en أو fr)
    return default_latin


class Segment(object):
    """مقطع نطق متجانس اللغة."""

    __slots__ = ("items", "lang")

    def __init__(self, items, lang):
        self.items = list(items)
        self.lang = lang

    def __repr__(self):
        return "Segment(lang=%r, items=%d)" % (self.lang, len(self.items))


import unicodedata

def detect_char_lang(c, default_latin="en"):
    """يحدد لغة حرف واحد."""
    cp = ord(c)
    for lo, hi in _ARABIC_RANGES:
        if lo <= cp <= hi: return "ar"
    for lo, hi in _CYRILLIC_RANGES:
        if lo <= cp <= hi: return "ru"
    for lo, hi in _HEBREW_RANGES:
        if lo <= cp <= hi: return "he"
    for lo, hi in _GREEK_RANGES:
        if lo <= cp <= hi: return "el"
    for lo, hi in _CJK_RANGES:
        if lo <= cp <= hi: return "zh"
    return default_latin

def split_sequence(speechSequence, default_lang="ar"):
    """يقسّم SpeechSequence إلى مقاطع متجانسة اللغة بدقة الحرف الواحد."""
    segments = []
    current_lang = default_lang
    current_items = []

    for item in speechSequence:
        if isinstance(item, str):
            sb = []
            for c in item:
                cat = unicodedata.category(c)
                # علامات الترقيم، الأرقام، المسافات، والرموز تتبع اللغة الحالية
                if cat.startswith("P") or cat.startswith("Z") or cat.startswith("S") or cat.startswith("M") or cat.startswith("N"):
                    new_lang = current_lang
                else:
                    new_lang = detect_char_lang(c, default_latin="en")
                
                if new_lang != current_lang:
                    if sb:
                        current_items.append("".join(sb))
                        sb = []
                    if current_items:
                        segments.append(Segment(current_items, current_lang))
                        current_items = []
                    current_lang = new_lang
                
                sb.append(c)
            
            if sb:
                current_items.append("".join(sb))
        else:
            current_items.append(item)

    if current_items:
        segments.append(Segment(current_items, current_lang))

    return segments
