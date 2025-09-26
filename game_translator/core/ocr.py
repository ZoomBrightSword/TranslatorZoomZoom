import pytesseract
import numpy as np
import cv2
from dataclasses import dataclass

@dataclass
class OcrResult:
    """
    Data contract for OCR results.
    """
    text: str
    confidence: float

class OcrEngine:
    """
    Handles Optical Character Recognition (OCR) using Tesseract.
    """
    def __init__(self, tesseract_cmd_path: str = None):
        """
        Initializes the OCR engine.

        Args:
            tesseract_cmd_path (str, optional): Path to the Tesseract executable.
                                                If None, it's assumed to be in the system's PATH.
        """
        if tesseract_cmd_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

        # You might need to specify language and other configs for better accuracy
        self.tesseract_config = r'--oem 3 --psm 6 -l eng'

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Applies pre-processing steps to the image to improve OCR accuracy.

        Args:
            image (np.ndarray): The input image (BGRA from mss).

        Returns:
            np.ndarray: The processed image (grayscale).
        """
        # Convert from BGRA to Grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)

        # Apply a slight blur to reduce noise
        # blurred = cv2.GaussianBlur(gray_image, (3, 3), 0)

        # Apply thresholding to get a binary image. This is crucial for OCR.
        # We use OTSU's binarization which automatically determines the threshold.
        _, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return binary_image

    def process_image(self, image: np.ndarray) -> OcrResult | None:
        """
        Performs OCR on a given image.

        Args:
            image (np.ndarray): The image to process.

        Returns:
            OcrResult | None: The result of the OCR, or None if no text is found.
        """
        if image is None:
            return None

        preprocessed_image = self._preprocess_image(image)

        try:
            # Use pytesseract to get detailed data, including confidence
            data = pytesseract.image_to_data(preprocessed_image, config=self.tesseract_config, output_type=pytesseract.Output.DICT)

            text_parts = []
            confidences = []

            # Filter out low-confidence results
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 50: # Confidence threshold
                    text = data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        confidences.append(int(data['conf'][i]))

            if not text_parts:
                return None

            full_text = " ".join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return OcrResult(text=full_text, confidence=avg_confidence)

        except pytesseract.TesseractNotFoundError:
            print("Tesseract Error: The Tesseract executable was not found.")
            print("Please install Tesseract and ensure it's in your system's PATH.")
            # We should probably signal this error to the UI.
            return OcrResult(text="TESSERACT NOT FOUND", confidence=0.0)
        except Exception as e:
            print(f"An unexpected error occurred in OCR: {e}")
            return None