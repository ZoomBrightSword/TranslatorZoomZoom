from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QApplication
from config import config_manager

class TranslationWindow(QWidget):
    """
    A separate, always-on-top window to display the translated text.
    """
    def __init__(self):
        super().__init__()
        self.current_font_size = config_manager.get("font_size", 12)

        # --- Window Configuration ---
        self.setWindowTitle("Translation")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setGeometry(100, 100, 500, 200) # x, y, width, height

        # --- Widgets ---
        self.layout = QVBoxLayout(self)
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.text_area.setAcceptRichText(False) # Plain text only
        self.layout.addWidget(self.text_area)
        self.setLayout(self.layout)

        # --- Styling ---
        self._apply_styles()
        self.update_font_size()

    def _apply_styles(self):
        """Applies basic styling to the window and text area."""
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QTextEdit {
                background-color: white;
                color: black;
                border: 1px solid #ccc;
            }
        """)

    @Slot(str)
    def update_text(self, text: str):
        """
        Public slot to update the text in the text area.
        This is connected to the orchestrator's signal.
        """
        self.text_area.setPlainText(text)
        # Scroll to the bottom to show the latest translation
        self.text_area.verticalScrollBar().setValue(self.text_area.verticalScrollBar().maximum())

    @Slot(str)
    def display_error(self, error_message: str):
        """
        Displays an error message in the text area with different styling.
        """
        self.text_area.setHtml(f"<font color='red'>{error_message}</font>")

    @Slot()
    def copy_translation_to_clipboard(self):
        """Copies the current text to the clipboard."""
        QApplication.clipboard().setText(self.text_area.toPlainText())
        self.display_error("Teks disalin ke clipboard.")

    @Slot()
    def increase_font_size(self):
        """Increases the font size."""
        self.current_font_size += 1
        self.update_font_size()

    @Slot()
    def decrease_font_size(self):
        """Decreases the font size, with a minimum size."""
        self.current_font_size = max(8, self.current_font_size - 1)
        self.update_font_size()

    def update_font_size(self):
        """Applies the current font size to the text area."""
        font = self.text_area.font()
        font.setPointSize(self.current_font_size)
        self.text_area.setFont(font)
        config_manager.set("font_size", self.current_font_size)
        # We can debounce this save call if needed
        config_manager.save()

    def closeEvent(self, event):
        """
        Save window position on close.
        In a real app, we might want to just hide it or ask the user.
        For now, closing this window will exit the app (as it's the main widget).
        """
        # A more robust implementation would handle closing the entire app
        # from main.py when this window is closed.
        QApplication.quit()
        super().closeEvent(event)