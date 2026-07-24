# -*- coding: UTF-8 -*-
"""PolyVoice - التبديل التلقائي السلس بين آلات النطق حسب لغة النص (NVDA 2026)."""

import addonHandler
import config

addonHandler.initTranslation()

# إعلان التوصيف القياسي لإعدادات PolyVoice في config.conf لـ NVDA 2026
confspec = {
    "enableAutoSwitch": "boolean(default=True)",
    "defaultLang": "string(default='ar')",
    "rate": "integer(default=50, min=0, max=100)",
    "pitch": "integer(default=50, min=0, max=100)",
    "volume": "integer(default=100, min=0, max=100)",
    "bindings": "__many__",
}

config.conf.spec["PolyVoice"] = confspec
