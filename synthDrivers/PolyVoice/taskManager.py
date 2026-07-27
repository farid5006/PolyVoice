# -*- coding: UTF-8 -*-
"""طبقة مدير المهام — تسلسل آمن ومستقر 100% ينقذ NVDA من الانهيار."""

import queue
import threading
from logHandler import log


class _SpeakTask(object):
    __slots__ = ("segment", "instance")

    def __init__(self, segment, instance=None):
        self.segment = segment
        self.instance = instance


class TaskManager(object):
    """يدير قائمة انتظار تسلسلية آمنة لمنع تداخل صوت الآلات ومنع الانهيار."""

    def __init__(self, voiceManager):
        self._vm = voiceManager
        self._q = queue.Queue()
        self._stopEvent = threading.Event()
        self._pauseEvent = threading.Event()
        self._currentTask = None
        self._lock = threading.Lock()
        self._synthLock = threading.Lock()

        try:
            self._workerThread = threading.Thread(
                target=self._worker, name="PolyVoice-Worker", daemon=True
            )
            self._workerThread.start()
        except Exception:
            log.exception("PolyVoice: فشل بدء خيط العامل")

    def enqueueSpeak(self, segment):
        self._q.put(_SpeakTask(segment))

    def pause(self, switch):
        if switch:
            self._pauseEvent.set()
        else:
            self._pauseEvent.clear()
        with self._synthLock:
            for instance in self._vm._instanceCache.values():
                try:
                    instance.pause(switch)
                except Exception:
                    pass

    def cancelAll(self):
        # 1. تفريغ قائمة المهام المحجوزة
        while True:
            try:
                self._q.get_nowait()
            except queue.Empty:
                break

        # 2. إيقاف الآلات النشطة فوراً
        with self._lock:
            task = self._currentTask
            self._currentTask = None

        # استخدام القفل لمنع تداخل أوامر الإيقاف مع النطق
        with self._synthLock:
            self._vm.cancelAll()

    def shutdown(self):
        self._stopEvent.set()
        self._q.put(None)
        if hasattr(self, "_workerThread"):
            self._workerThread.join(timeout=1.0)

    def _worker(self):
        while not self._stopEvent.is_set():
            try:
                task = self._q.get(timeout=0.05)
            except queue.Empty:
                continue
            if task is None:
                break
            self._runTask(task)

    def _runTask(self, task):
        instance = self._vm.get_voice_instance(task.segment.lang)
        if instance is None:
            return
        task.instance = instance

        while self._pauseEvent.is_set() and not self._stopEvent.is_set():
            self._pauseEvent.wait(timeout=0.05)
        if self._stopEvent.is_set():
            return

        with self._lock:
            self._currentTask = task

        # ممتص صدمات (Debounce) لامتصاص الأوامر المتلاحقة عند التنقل السريع
        import time
        time.sleep(0.03)  # تأخير 30 ملي ثانية

        with self._lock:
            # إذا تم تفريغ المهمة بواسطة cancelAll أثناء فترة الانتظار، نتجاهل النطق
            if self._currentTask is not task:
                return

        try:
            # تنفيذ النطق بصورة آمنة ومستقرة داخل القفل لمنع تداخل الإيقاف
            with self._synthLock:
                instance.speak(task.segment.items)
        except Exception:
            log.exception("PolyVoice: استثناء أثناء تنفيذ نطق المقطع")
        finally:
            with self._lock:
                if self._currentTask is task:
                    self._currentTask = None
