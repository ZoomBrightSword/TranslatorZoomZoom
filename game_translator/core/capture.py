import mss
import numpy as np
from utils.logger import log

class CaptureEngine:
    """
    Handles screen capturing using the `mss` library.
    """
    def __init__(self):
        """
        Initializes the screen capture engine.
        """
        self.sct = mss.mss()
        self.capture_area = {"top": 100, "left": 100, "width": 400, "height": 200}
        log.info("CaptureEngine initialized.")

    def set_capture_area(self, rect: list[int]):
        """
        Sets the screen area to be captured.

        Args:
            rect (list[int]): A list containing [x, y, width, height].
        """
        if rect and len(rect) == 4:
            self.capture_area = {"left": rect[0], "top": rect[1], "width": rect[2], "height": rect[3]}
            log.info(f"Capture area set to: {self.capture_area}")

    def capture_frame(self) -> np.ndarray | None:
        """
        Captures a single frame from the defined screen area.

        Returns:
            np.ndarray | None: The captured image as a NumPy array in BGRA format,
                              or None if the capture area is invalid.
        """
        if self.capture_area["width"] <= 0 or self.capture_area["height"] <= 0:
            return None

        try:
            # Grab the data
            sct_img = self.sct.grab(self.capture_area)
            # Convert to a NumPy array
            img = np.array(sct_img)
            return img
        except mss.exception.ScreenShotError as e:
            log.error(f"Error during screen capture: {e}")
            return None

    def close(self):
        """
        Closes the mss instance.
        """
        self.sct.close()