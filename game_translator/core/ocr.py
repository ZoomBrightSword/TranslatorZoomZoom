import pytesseract
import numpy as np
import cv2
from dataclasses import dataclass
from config import config_manager
from utils.logger import log

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
    Supports different quality settings for preprocessing.
    """
    def __init__(self, tesseract_cmd_path: str = None):
        """
        Initializes the OCR engine.
        """
        if tesseract_cmd_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path
        self.tesseract_config = r'--oem 3 --psm 6 -l eng'

    def _preprocess_image(self, image: np.ndarray, quality: str, primary: bool) -> np.ndarray:
        """
        Applies pre-processing steps to the image based on the quality and attempt.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)

        if primary:
            # --- Primary Attempt ---
            if quality == "quality":
                # Upscale, denoise, then use Otsu's thresholding
                h, w = gray.shape
                upscaled = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
                denoised = cv2.fastNlMeansDenoising(upscaled, None, h=10, templateWindowSize=7, searchWindowSize=21)
                _, binary_image = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                return binary_image
            else:
                # Simple global thresholding for speed
                _, binary_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                return binary_image
        else:
            # --- Fallback Attempt ---
            # Use adaptive thresholding, which is good for uneven lighting
            # but can be slower.
            return cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

    def process_image(self, image: np.ndarray) -> OcrResult | None:
        """
        Performs OCR on a given image, using the configured quality setting.
        """
        if image is None:
            return None

        # Get quality setting from the config manager
        quality = config_manager.get("ocr_quality", "speed")

        # --- Primary OCR Attempt ---
        preprocessed_image = self._preprocess_image(image, quality, primary=True)
        result = self._perform_ocr_on_image(preprocessed_image)

        # --- Fallback OCR Attempt ---
        # If the primary attempt fails, try a different preprocessing strategy
        if result is None:
            log.info("Primary OCR failed. Trying fallback preprocessing...")
            fallback_image = self._preprocess_image(image, quality, primary=False)
            result = self._perform_ocr_on_image(fallback_image)
            if result:
                log.info("Fallback OCR successful.")

        return result

    def _perform_ocr_on_image(self, image: np.ndarray) -> OcrResult | None:
        """Helper function to run Tesseract on a preprocessed image."""
        try:
            data = pytesseract.image_to_data(image, config=self.tesseract_config, output_type=pytesseract.Output.DICT)

            text_parts = []
            confidences = []

            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 50:
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
            log.error("Tesseract Error: The Tesseract executable was not found. Please install Tesseract and ensure it's in your system's PATH.")
            # We should probably signal this error to the UI.
            return OcrResult(text="TESSERACT NOT FOUND", confidence=0.0)
        except Exception as e:
            log.error(f"An unexpected error occurred in OCR: {e}")
            return None