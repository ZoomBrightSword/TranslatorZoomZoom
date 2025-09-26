from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QApplication
from config import config_manager
from core.models import PipelineResult, PipelineStatus

class TranslationWindow(QWidget):
    """
    A separate, always-on-top window to display translated text and status.
    """
    def __init__(self):
        super().__init__()
        self.current_font_size = config_manager.get("font_size", 12)

        # --- Window Configuration ---
        self.setWindowTitle("Translation")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setGeometry(100, 100, 500, 220) # Increased height for status bar

        # --- Widgets ---
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)

        self.status_bar = QLabel("Menginisialisasi...", self)

        self.layout.addWidget(self.text_area)
        self.layout.addWidget(self.status_bar)
        self.setLayout(self.layout)

        # --- Styling ---
        self._apply_styles()
        self.update_font_size()

    def _apply_styles(self):
        """Applies basic styling to the window and widgets."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QTextEdit {
                background-color: white;
                color: black;
                border: 1px solid #ccc;
                font-family: Arial, sans-serif;
            }
            QLabel {
                color: #555;
                font-size: 9pt;
            }
        """)

    @Slot(object)
    def update_view(self, result: PipelineResult):
        """
        Public slot to update the entire view based on a PipelineResult object.
        """
        # Update the main text area only if there's new text
        if result.text:
            self.text_area.setPlainText(result.text)
            # Scroll to the bottom to show the latest translation
            self.text_area.verticalScrollBar().setValue(self.text_area.verticalScrollBar().maximum())

        # Handle error state
        if result.status == PipelineStatus.ERROR:
            self.text_area.setHtml(f"<font color='red'><b>Error:</b> {result.error_message}</font>")
            self.status_bar.setText(f"Status: Error")
            return

        # Update status bar
        status_text = f"Status: {result.get_status_message()}"
        if result.processing_time_ms > 0:
            status_text += f" | Waktu: {result.processing_time_ms:.0f} ms"

        self.status_bar.setText(status_text)

    @Slot()
    def copy_translation_to_clipboard(self):
        """Copies the current text to the clipboard."""
        QApplication.clipboard().setText(self.text_area.toPlainText())
        # Provide feedback via the status bar
        self.status_bar.setText("Teks disalin ke clipboard.")

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
        config_manager.save()

    def closeEvent(self, event):
        """Ensures the application quits when this window is closed."""
        QApplication.quit()
        super().closeEvent(event)