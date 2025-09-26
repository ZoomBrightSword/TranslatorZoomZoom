from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QGuiApplication
from PySide6.QtWidgets import QWidget
from config import config_manager

class OverlayWindow(QWidget):
    """
    A transparent, always-on-top window for selecting a screen area.
    It's click-through unless in selection mode.
    """
    # Signal emitted when a new area is selected by the user.
    # The signal carries the QRect of the selected area.
    capture_area_selected = Signal(list)

    def __init__(self):
        super().__init__()
        self.is_selecting = False
        self.selection_rect = QRect()
        self.start_point = None
        self.end_point = None

        # --- Window Configuration ---
        # Make the window borderless, always on top, and transparent
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool # Prevents the window from appearing in the taskbar
        )
        # Make the background translucent
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Pass mouse events through to the window below (the game)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Set the window to span all available screens
        self.setGeometry(QGuiApplication.primaryScreen().virtualGeometry())

        # Load the last capture area from config
        self._load_initial_rect()

    def _load_initial_rect(self):
        """Loads the capture area from the config file on startup."""
        rect_coords = config_manager.get("capture_area")
        if rect_coords:
            self.selection_rect = QRect(*rect_coords)
            self.update() # Trigger a repaint

    def start_selection_mode(self):
        """
        Activates selection mode, making the window interactive.
        """
        print("Starting selection mode.")
        self.is_selecting = True
        # Make the window temporarily interactive
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setCursor(Qt.CrossCursor)
        # Show a semi-transparent overlay to indicate selection mode
        self.update()

    def stop_selection_mode(self):
        """
        Deactivates selection mode and makes the window click-through again.
        """
        print("Stopping selection mode.")
        self.is_selecting = False
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.unsetCursor()
        self.update()

    def toggle_visibility(self):
        """Shows or hides the overlay window."""
        self.setVisible(not self.isVisible())

    def paintEvent(self, event):
        """
        Paints the window. This is where the magic happens.
        """
        painter = QPainter(self)

        if self.is_selecting:
            # Draw a semi-transparent black overlay
            painter.fillRect(self.rect(), QColor(0, 0, 0, 70))
            # Draw the currently dragged rectangle
            if self.start_point and self.end_point:
                selection = QRect(self.start_point, self.end_point).normalized()
                painter.setPen(QPen(QColor(255, 255, 255), 1, Qt.DashLine))
                painter.drawRect(selection)
        else:
            # When not selecting, just draw a border around the capture area
            painter.setPen(QPen(QColor(255, 0, 0, 200), 2, Qt.SolidLine)) # Bright red border
            painter.drawRect(self.selection_rect)

    def mousePressEvent(self, event):
        """Handles the start of a drag selection."""
        if self.is_selecting and event.button() == Qt.LeftButton:
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            self.update()

    def mouseMoveEvent(self, event):
        """Handles the dragging action to define the rectangle."""
        if self.is_selecting and event.buttons() & Qt.LeftButton:
            self.end_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        """Handles the end of a drag selection."""
        if self.is_selecting and event.button() == Qt.LeftButton:
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()

            # Emit the signal with the rectangle's coordinates
            rect_list = [
                self.selection_rect.x(),
                self.selection_rect.y(),
                self.selection_rect.width(),
                self.selection_rect.height()
            ]
            self.capture_area_selected.emit(rect_list)

            self.stop_selection_mode()
            self.start_point = None
            self.end_point = None