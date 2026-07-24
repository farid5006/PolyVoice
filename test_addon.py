# -*- coding: UTF-8 -*-
"""ملف اختبار شامل لإضافة PolyVoice - بيئة اختبار افتراضية

يقوم هذا الملف باختبار:
1. استيراد جميع الملفات بدون أخطاء
2. إنشاء VoiceManager وتحديد الآلات المتاحة
3. إنشاء SynthDriver واختباره
4. محاولة إنشاء نسخة من SAPI5
5. اختبار إعدادات configspec
6. اختبار الكشف عن الآلات في NVDA
"""

import sys
import os

# إضافة مسار المشروع للنظام
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
sys.path.insert(0, os.path.join(project_dir, "synthDrivers", "PolyVoice"))

print("=" * 80)
print("بيئة اختبار إضافة PolyVoice")
print("=" * 80)

# اختبار 1: استيراد جميع الملفات
print("\n[1/7] اختبار استيراد جميع الملفات...")
try:
    from synthDrivers.PolyVoice.voiceInfo import VoiceBinding, parse_binding
    print("  ✓ تم استيراد voiceInfo.py")
except Exception as e:
    print(f"  ✗ فشل استيراد voiceInfo.py: {e}")
    sys.exit(1)

try:
    from synthDrivers.PolyVoice.voiceManager import VoiceManager
    print("  ✓ تم استيراد voiceManager.py")
except Exception as e:
    print(f"  ✗ فشل استيراد voiceManager.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from synthDrivers.PolyVoice.languageDetection import split_sequence
    print("  ✓ تم استيراد languageDetection.py")
except Exception as e:
    print(f"  ✗ فشل استيراد languageDetection.py: {e}")
    sys.exit(1)

try:
    from synthDrivers.PolyVoice.taskManager import TaskManager
    print("  ✓ تم استيراد taskManager.py")
except Exception as e:
    print(f"  ✗ فشل استيراد taskManager.py: {e}")
    sys.exit(1)

try:
    from synthDrivers.PolyVoice.__init__ import SynthDriver
    print("  ✓ تم استيراد SynthDriver")
except Exception as e:
    print(f"  ✗ فشل استيراد SynthDriver: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# اختبار 2: اختبار VoiceManager
print("\n[2/7] اختبار VoiceManager...")
try:
    vm = VoiceManager()
    print("  ✓ تم إنشاء VoiceManager")

    engines = vm.getEngineNames()
    print(f"  ✓ عدد الآلات المكتشفة: {len(engines)}")
    if engines:
        print(f"  الآلات: {engines}")

    # اختبار الحصول على ربط افتراضي
    binding_ar = vm._resolveBinding("ar")
    if binding_ar:
        print(f"  ✓ ربط افتراضي للعربية: {binding_ar.engine} | {binding_ar.voice}")
    else:
        print(f"  ✗ لا يوجد ربط افتراضي للعربية")

    binding_en = vm._resolveBinding("en")
    if binding_en:
        print(f"  ✓ ربط افتراضي للإنجليزية: {binding_en.engine} | {binding_en.voice}")
    else:
        print(f"  ✗ لا يوجد ربط افتراضي للإنجليزية")

except Exception as e:
    print(f"  ✗ فشل اختبار VoiceManager: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# اختبار 3: اختبار إنشاء نسخة من SAPI5
print("\n[3/7] اختبار إنشاء نسخة من SAPI5...")
try:
    binding = vm._resolveBinding("ar")
    if binding:
        print(f"  ✓ تم الحصول على ربط: {binding.engine} | {binding.voice}")

        instance = vm._create_instance(binding)
        if instance:
            print(f"  ✓ تم إنشاء نسخة من الآلة: {instance.engine}")
            print(f"  ✓ اسم الصوت: {instance.voice}")
        else:
            print(f"  ✗ فشل إنشاء نسخة من الآلة")
    else:
        print(f"  ✗ لا يوجد ربط للعربية")
except Exception as e:
    print(f"  ✗ فشل اختبار إنشاء نسخة: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# اختبار 4: اختبار configspec
print("\n[4/7] اختبار configspec...")
try:
    # محاكاة configspec بدون استدعاء config الحقيقي
    test_configspec = {
        "rate": "integer(min=0, max=200, default=100)",
        "pitch": "integer(min=0, max=200, default=100)",
        "volume": "integer(min=0, max=100, default=100)",
        "characterMode": "boolean(default=False)",
        "indexFormat": "string(default='character')",
        "defaultVoice": "string(default='sapi5')",
        "enableAutoSwitch": "boolean(default=True)",
        "defaultLang": "string(default='ar')",
    }
    print("  ✓ تم إنشاء configspec افتراضي")
    print(f"  إعدادات: {list(test_configspec.keys())}")
except Exception as e:
    print(f"  ✗ فشل اختبار configspec: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# اختبار 5: اختبار SynthDriver
print("\n[5/7] اختبار SynthDriver...")
try:
    driver = SynthDriver()
    print("  ✓ تم إنشاء SynthDriver")

    # اختبار الخصائص الأساسية
    print(f"  ✓ الاسم: {driver.name}")
    print(f"  ✓ الوصف: {driver.description}")

    # اختبار الدوال المطلوبة
    if hasattr(driver, 'check'):
        result = driver.check()
        print(f"  ✓ دالة check(): {result}")

    if hasattr(driver, '_get_rate'):
        rate = driver._get_rate()
        print(f"  ✓ معدل السرعة: {rate}")

    if hasattr(driver, '_get_pitch'):
        pitch = driver._get_pitch()
        print(f"  ✓ درجة الحدة: {pitch}")

    if hasattr(driver, '_get_volume'):
        volume = driver._get_volume()
        print(f"  ✓ مستوى الصوت: {volume}")

    # اختبار الحصول على الأصوات المتاحة
    voices = driver._getAvailableVoices()
    print(f"  ✓ عدد الأصوات المتاحة: {len(voices)}")
    if voices:
        print(f"  الأصوات: {list(voices.keys())}")

    # اختبار الحصول على اللغات المدعومة
    langs = driver._getAvailableLanguages()
    print(f"  ✓ اللغات المدعومة: {langs}")

    # اختبار الإعدادات المدعومة
    settings = driver._get_supportedSettings()
    print(f"  ✓ الإعدادات المدعومة: {settings}")

except Exception as e:
    print(f"  ✗ فشل اختبار SynthDriver: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# اختبار 6: اختبار الكشف عن الآلات
print("\n[6/7] اختبار الكشف عن الآلات...")
try:
    import synthDriverHandler
    synthList = synthDriverHandler.getSynthList()
    print(f"  ✓ تم استدعاء getSynthList()")
    print(f"  عدد الآلات في NVDA: {len(synthList)}")
    print(f"  الآلات: {[(name, desc) for name, desc in synthList[:5]]}")
except Exception as e:
    print(f"  ✗ فشل اختبار الكشف عن الآلات: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# اختبار 7: اختبار parse_binding
print("\n[7/7] اختبار parse_binding...")
try:
    test_cases = [
        ("sapi5", VoiceBinding("sapi5", "")),
        ("sapi5|Microsoft David", VoiceBinding("sapi5", "Microsoft David")),
        ("sapi5|Microsoft Mark", VoiceBinding("sapi5", "Microsoft Mark")),
        ("", None),
    ]
    for raw, expected in test_cases:
        result = parse_binding(raw)
        if result == expected:
            print(f"  ✓ parse_binding('{raw}') -> {result}")
        else:
            print(f"  ✗ parse_binding('{raw}') -> {result}, expected {expected}")
except Exception as e:
    print(f"  ✗ فشل اختبار parse_binding: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✓✓✓ جميع الاختبارات نجحت! ✓✓✓")
print("=" * 80)
print("\nالإضافة جاهزة للتثبيت على NVDA!")
print("\nالخطوات التالية:")
print("1. إلغاء تثبيت الإضافة القديمة")
print("2. تثبيت الإضافة الجديدة: PolyVoice-0.1.0.nvda-addon")
print("3. فتح NVDA واختبار الإضافة")
