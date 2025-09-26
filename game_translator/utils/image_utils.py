import numpy as np
import cv2

def check_for_significant_change(img1: np.ndarray, img2: np.ndarray, threshold: int = 10) -> bool:
    """
    Compares two images to detect if there has been a significant change.
    This can be used as an optimization to avoid running OCR if the screen
    area has not visually changed.

    Args:
        img1 (np.ndarray): The first image.
        img2 (np.ndarray): The second image.
        threshold (int): The sensitivity for change detection. A lower value
                         means more sensitivity.

    Returns:
        bool: True if a significant change is detected, False otherwise.
    """
    if img1 is None or img2 is None:
        return True # Assume change if one image is missing

    # Ensure images are the same size and type
    if img1.shape != img2.shape or img1.dtype != img2.dtype:
        return True # Shapes differ, so it's a change

    # Convert to grayscale for simplicity
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGRA2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGRA2GRAY)

    # Compute the absolute difference
    diff = cv2.absdiff(gray1, gray2)

    # Calculate the percentage of non-zero pixels
    non_zero_count = np.count_nonzero(diff)
    total_pixels = diff.shape[0] * diff.shape[1]

    if total_pixels == 0:
        return False

    change_percentage = (non_zero_count / total_pixels) * 100

    return change_percentage > threshold