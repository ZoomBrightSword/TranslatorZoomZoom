import sys
from PySide6.QtWidgets import QApplication
from ui.overlay_window import OverlayWindow
from ui.translation_window import TranslationWindow
from core.orchestrator import Orchestrator
from core.hotkey_manager import HotkeyManager

def main():
    """
    Main entry point for the application.
    Initializes the Qt application, windows, and core components.
    """
    app = QApplication(sys.argv)

    # --- Create Core Components ---
    # The orchestrator will manage the capture-ocr-translate pipeline
    orchestrator = Orchestrator()

    # --- Create UI Components ---
    # Translation window to display results
    translation_window = TranslationWindow()
    # Overlay window for selecting capture area
    overlay_window = OverlayWindow()

    # --- Wire up signals and slots ---
    # Connect orchestrator's translation result to the translation window
    orchestrator.new_translation_ready.connect(translation_window.update_text)
    orchestrator.error_occurred.connect(translation_window.display_error)

    # Connect overlay's area selection to the orchestrator
    overlay_window.capture_area_selected.connect(orchestrator.set_capture_area)

    # --- Setup and Start Hotkeys ---
    # Hotkeys need to control the visibility of the overlay and start/stop the orchestrator
    hotkey_manager = HotkeyManager()
    hotkey_manager.toggle_overlay.connect(overlay_window.toggle_visibility)
    hotkey_manager.toggle_capture.connect(orchestrator.toggle_capture)
    hotkey_manager.select_area.connect(overlay_window.start_selection_mode)

    # Connect hotkeys for translation window controls
    hotkey_manager.copy_translation.connect(translation_window.copy_translation_to_clipboard)
    hotkey_manager.increase_font.connect(translation_window.increase_font_size)
    hotkey_manager.decrease_font.connect(translation_window.decrease_font_size)

    hotkey_manager.start()

    # --- Show Windows ---
    translation_window.show()
    overlay_window.show()

    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()