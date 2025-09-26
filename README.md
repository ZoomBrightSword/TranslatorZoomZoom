# Game Translator - Real-time Game Translation Overlay

This application provides a real-time translation overlay for games, capturing on-screen English text and displaying its Indonesian translation in a separate window.

## 1. Architecture & Technology Stack

### 1.1. Chosen Stack: Python

The application is built using **Python** with the following core libraries:

-   **UI Framework**: `PySide6` (the official Qt for Python bindings).
    -   **Pro**: Excellent cross-platform support (though we target Windows), powerful styling capabilities, mature, and provides all necessary components for creating complex UIs like transparent, borderless, always-on-top windows.
    -   **Con**: Can have a slightly steeper learning curve than simpler toolkits, but its power is necessary for this project's requirements.
-   **Screen Capture**: `mss` (fastest pure Python screen capture) combined with `ctypes` for WinAPI calls where necessary.
    -   **Pro**: `mss` is incredibly fast. For advanced features like hardware-accelerated capture (Windows Graphics Capture), we can use Python wrappers like `pygrabber` or direct `ctypes` calls, staying within the Python ecosystem. This avoids process injection and is anti-cheat friendly.
    -   **Con**: Direct access to Desktop Duplication API requires more complex `ctypes` work compared to C#.
-   **OCR**: `Tesseract` via `pytesseract` wrapper.
    -   **Pro**: Highly accurate for printed English text, mature, and runs locally. It's the industry standard for open-source OCR. We can later explore `PaddleOCR` if Tesseract has issues with specific game fonts.
    -   **Con**: Can be slow if not configured correctly (e.g., processing large areas). Performance will depend on pre-processing.
-   **Translation**: `ctranslate2` with a MarianMT model (EN-ID).
    -   **Pro**: Runs entirely locally, very fast, and provides good quality for many language pairs. This avoids reliance on external APIs and associated costs/latency.
    -   **Con**: Model needs to be downloaded (~300MB). Translation quality might be less nuanced than large cloud-based models like DeepL or Google Translate for complex sentences.
-   **Hotkeys**: `pynput`.
    -   **Pro**: Simple, cross-platform, and runs in a separate thread, preventing the UI from freezing.

### 1.2. Application Architecture

The application uses a multi-threaded, two-window architecture:

1.  **Overlay Window (`OverlayWindow`)**: A transparent, click-through, borderless window that is always on top. Its only purpose is to display the user-selected capture area. The user can drag a rectangle on this window to define the region to be translated.
2.  **Translation Window (`TranslationWindow`)**: A standard, opaque, always-on-top window. It displays the translated text. It is draggable, resizable, and has a simple white background with black text.
3.  **Orchestrator (`Orchestrator`)**: A core background thread that runs the main processing pipeline. It communicates with the UI windows using Qt's signal/slot mechanism to avoid race conditions and ensure thread safety.

---

## 2. Processing Pipeline

The pipeline is executed by the `Orchestrator` thread in a continuous loop (when active).

`[Capture Screen Area] -> [Pre-process Image] -> [Perform OCR] -> [Check for Text Change] -> [Translate Text] -> [Post-process & Glossary] -> [Render in UI]`

1.  **Capture**: Captures the defined rectangular area of the screen.
    -   *Estimated Latency*: 10-50 ms (highly dependent on screen resolution and capture method).
2.  **Image Pre-processing**: Converts the image to grayscale and applies thresholding to improve OCR accuracy.
    -   *Estimated Latency*: 5-15 ms.
3.  **OCR**: The pre-processed image is sent to Tesseract to extract text.
    -   *Estimated Latency*: 100-300 ms (This is the main bottleneck. Optimization: run OCR only when motion is detected in the area).
4.  **Text Diffing**: The extracted text is hashed. If the hash is the same as the previous frame's hash, the pipeline stops to prevent re-translation. A debounce mechanism prevents rapid, minor changes from triggering too many translations.
    -   *Estimated Latency*: <1 ms.
5.  **Translate**: If the text is new, it's sent to the local CTranslate2 model.
    -   *Estimated Latency*: 50-150 ms.
6.  **Post-processing & Glossary**:
    -   The translated text is cleaned (e.g., fixing line breaks).
    -   The glossary is applied to replace specific game terms for consistency.
    -   *Estimated Latency*: <5 ms.
7.  **Render**: The final text is sent to the `TranslationWindow` via a Qt signal.
    -   *Estimated Latency*: <10 ms.

**Total Target Latency**: 200-500 ms.

---

## 3. Module Interfaces & Data Contracts

-   `capture.py`: `CaptureEngine` class
    -   `set_capture_area(rect: tuple[int, int, int, int])`
    -   `capture_frame() -> np.ndarray` (returns a NumPy array of the image)
-   `ocr.py`: `OcrEngine` class
    -   `process_image(image: np.ndarray) -> OcrResult`
-   `translator.py`: `TranslatorEngine` class
    -   `load_glossary(path: str)`
    -   `translate(text: str) -> str`
-   `orchestrator.py`: `Orchestrator(QObject)`
    -   `start()`, `stop()`, `set_capture_area()`
    -   Signals: `new_translation_ready(str)`, `error_occured(str)`

**Data Contract (`OcrResult`)**:
A `dataclass` or `TypedDict` will be used.
```python
class OcrResult:
    text: str
    confidence: float
    # Potentially add bounding boxes later if needed
    # bboxes: list[tuple[int, int, int, int]]
```

---

## 4. Core UX/System Strategies

-   **Transparency & Click-Through**: The `OverlayWindow` will use Qt's `Qt.WindowTransparentForInput` and `Qt.WA_TranslucentBackground` flags. This makes the window itself invisible and allows mouse clicks to "pass through" to the game behind it. A thin, colored frame will be painted on the window to visualize the capture area.
-   **Always-on-Top**: Both windows will use the `Qt.WindowStaysOnTopHint` flag.
-   **Area Selection**:
    1.  User presses `Ctrl+Shift+3` hotkey.
    2.  The `OverlayWindow` becomes opaque (e.g., 30% black) and is no longer click-through.
    3.  The user clicks and drags to draw a rectangle.
    4.  On mouse release, the rectangle's coordinates are saved to the config file and sent to the `Orchestrator`.
    5.  The window returns to its transparent, click-through state.
-   **Configuration**: All settings (last capture area, font size, etc.) will be stored in `%APPDATA%/GameTranslator/config.json`. The app will create this on first launch.

---

## 5. Dependencies & Setup

**Dependencies will be listed in `requirements.txt`.**

**Development Environment Setup**:
1.  Install Python 3.9+.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate it: `source venv/bin/activate` (Linux/macOS) or `.\venv\Scripts\activate` (Windows).
4.  Install Tesseract OCR engine from official installers. Ensure `tesseract.exe` is in the system's PATH.
5.  Install Python packages: `pip install -r requirements.txt`.
6.  Download the MarianMT EN-ID model for CTranslate2. A script will be provided to handle this.
7.  Run the application: `python game_translator/main.py`.