from pynput import keyboard
from PySide6.QtCore import QObject, Signal

class HotkeyManager(QObject):
    """
    Manages global hotkeys using pynput and emits Qt signals.
    This runs in a separate thread to not block the main application.
    """
    # --- Qt Signals ---
    # These signals will be connected to slots in the UI or core components
    toggle_overlay = Signal()
    toggle_capture = Signal()
    select_area = Signal()
    # Example for font size adjustment
    increase_font = Signal()
    decrease_font = Signal()
    copy_translation = Signal()

    def __init__(self):
        """
        Initializes the hotkey manager.
        """
        super().__init__()
        self.listener = None

        # Define the hotkeys
        self.hotkeys = {
            '<ctrl>+<shift>+1': self.toggle_overlay.emit,
            '<ctrl>+<shift>+2': self.toggle_capture.emit,
            '<ctrl>+<shift>+3': self.select_area.emit,
            '<ctrl>+<shift>+c': self.copy_translation.emit,
            '<ctrl>+<shift>+up': self.increase_font.emit,
            '<ctrl>+<shift>+down': self.decrease_font.emit,
        }

    def _on_press(self, key):
        """
        Callback function for when a key is pressed.
        """
        try:
            # Get the string representation for the pressed key combination
            key_combination = keyboard.HotKey.normalize(self.listener.canonical(key))

            if key_combination in self.hotkeys:
                # If the key combination is a registered hotkey, emit the corresponding signal
                self.hotkeys[key_combination]()

        except Exception as e:
            print(f"Error processing key press: {e}")

    def start(self):
        """
        Starts the keyboard listener in a non-blocking way.
        """
        if self.listener is None:
            self.listener = keyboard.Listener(on_press=self._on_press)
            self.listener.start()
            print("Hotkey listener started.")

    def stop(self):
        """
        Stops the keyboard listener.
        """
        if self.listener:
            self.listener.stop()
            self.listener = None
            print("Hotkey listener stopped.")