# -*- coding: UTF-8 -*-
"""ملف اختبار لـ VoiceManager للتحقق من الأخطاء في وقت مبكر."""

import sys
import os

# إضافة مسار المشروع للنظام
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "synthDrivers", "PolyVoice"))

try:
	from voiceManager import VoiceManager
	print("✓ تم استيراد VoiceManager بنجاح")

	# محاولة إنشاء مثيل
	vm = VoiceManager()
	print("✓ تم إنشاء VoiceManager بنجاح")

	# محاولة الحصول على قائمة الآلات
	engines = vm.getAvailableEngines()
	print("✓ تم الحصول على قائمة الآلات:")
	for name, desc in engines:
		print(f"  - {name}: {desc}")

	# محاولة الحصول على أسماء الآلات
	engineNames = vm.getEngineNames()
	print(f"✓ عدد الآلات المكتشفة: {len(engineNames)}")

	# محاولة الحصول على ربط افتراضي
	binding = vm._resolveBinding("ar")
	if binding:
		print(f"✓ ربط افتراضي للغة العربية: {binding.engine} | {binding.voice}")
	else:
		print("✓ لم يتم العثور على ربط افتراضي للغة العربية")

	print("\n✅ جميع الاختبارات نجحت!")

except SyntaxError as e:
	print(f"❌ خطأ في السينتاكس: {e}")
	sys.exit(1)

except IndentationError as e:
	print(f"❌ خطأ في الإزاحة (IndentationError): {e}")
	sys.exit(1)

except Exception as e:
	print(f"❌ خطأ غير متوقع: {e}")
	import traceback
	traceback.print_exc()
	sys.exit(1)
