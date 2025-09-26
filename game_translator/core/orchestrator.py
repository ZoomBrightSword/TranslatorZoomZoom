import time
import hashlib
from PySide6.QtCore import QObject, Signal, QThread
from core.capture import CaptureEngine
from core.ocr import OcrEngine
from core.translation_manager import TranslationManager
from config import config_manager
from utils.text_utils import clean_text

# --- Worker Class for the Pipeline ---
class PipelineWorker(QObject):
    """
    This worker object will run the main processing loop in a separate thread.
    """
    # Signals to communicate with the main thread (UI)
    new_translation_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.is_paused = True
        self.last_text_hash = None
        self.debounce_time = 0.2  # 200ms debounce
        self.last_capture_time = 0

        # Initialize core components
        self.capture_engine = CaptureEngine()
        self.ocr_engine = OcrEngine()
        self.translation_manager = TranslationManager()

        # Load the glossary on startup
        glossary_path = "game_translator/assets/glossary.json"
        self.translation_manager.load_glossary(glossary_path)

    def run(self):
        """
        The main processing loop. This will be executed by the QThread.
        """
        self.is_running = True
        while self.is_running:
            if self.is_paused:
                time.sleep(0.5)  # Sleep when paused to reduce CPU usage
                continue

            # --- Main Pipeline ---
            # 1. Capture
            frame = self.capture_engine.capture_frame()
            if frame is None:
                time.sleep(0.1)
                continue

            # 2. OCR
            ocr_result = self.ocr_engine.process_image(frame)
            if not ocr_result or not ocr_result.text:
                time.sleep(0.1)
                continue

            # 3. Clean and Hash Text
            cleaned_text = clean_text(ocr_result.text)
            current_text_hash = hashlib.md5(cleaned_text.encode()).hexdigest()

            # 4. Diffing (check if text has changed)
            if current_text_hash != self.last_text_hash:
                # Debounce: wait a bit to see if text settles
                if time.time() - self.last_capture_time > self.debounce_time:
                    self.last_text_hash = current_text_hash

                    # 5. Translate
                    translated_text = self.translation_manager.translate(cleaned_text)
                    if translated_text:
                        # 6. Emit result
                        self.new_translation_ready.emit(translated_text)

                    self.last_capture_time = time.time()

            # Limit FPS
            time.sleep(1 / 15) # Cap at ~15 FPS

    def stop(self):
        """Stops the processing loop."""
        self.is_running = False

# --- Main Orchestrator Class ---
class Orchestrator(QObject):
    """
    Manages the pipeline worker and thread, and provides a clean interface
    for the rest of the application.
    """
    # Expose signals from the worker
    new_translation_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self._thread = QThread()
        self._worker = PipelineWorker()

        # Move worker to the thread
        self._worker.moveToThread(self._thread)

        # Connect signals
        self._worker.new_translation_ready.connect(self.new_translation_ready)
        self._worker.error_occurred.connect(self.error_occurred)
        self._thread.started.connect(self._worker.run)

        # Load initial config
        initial_area = config_manager.get("capture_area")
        self._worker.capture_engine.set_capture_area(initial_area)

        # Start the thread
        self._thread.start()

    def set_capture_area(self, rect: list[int]):
        """Public method to set the capture area on the worker."""
        self._worker.capture_engine.set_capture_area(rect)
        config_manager.set("capture_area", rect)
        config_manager.save()

    def toggle_capture(self):
        """Starts or pauses the capture pipeline."""
        self._worker.is_paused = not self._worker.is_paused
        status = "PAUSED" if self._worker.is_paused else "RUNNING"
        print(f"Capture state changed to: {status}")
        if self._worker.is_paused:
            self.new_translation_ready.emit(f"Penerjemahan dijeda. Tekan Ctrl+Shift+2 untuk melanjutkan.")
        else:
            self.new_translation_ready.emit(f"Penerjemahan dimulai...")
            self._worker.last_text_hash = None # Reset hash to force translation

    def __del__(self):
        """Ensure the thread is cleaned up properly."""
        self._worker.stop()
        self._thread.quit()
        self._thread.wait()