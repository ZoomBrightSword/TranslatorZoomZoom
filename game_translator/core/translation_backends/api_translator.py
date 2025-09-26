import requests
import time
import json
from ...utils.logger import log

# Public LibreTranslate API endpoint from a known mirror
API_URL = "https://translate.argosopentech.com/translate"

class ApiTranslator:
    """
    A translation backend that uses a public LibreTranslate API.
    Includes robust error handling and retry logic.
    """
    def __init__(self, retries=3, backoff_factor=0.5):
        self.retries = retries
        self.backoff_factor = backoff_factor
        log.info("API Translator (LibreTranslate) initialized.")

    def translate(self, text: str) -> str | None:
        if not text:
            return None

        payload = {"q": text, "source": "en", "target": "id", "format": "text"}

        for attempt in range(self.retries):
            try:
                response = requests.post(API_URL, json=payload, timeout=10)
                response.raise_for_status()  # Raise for 4xx/5xx status codes

                try:
                    data = response.json()
                    if "translatedText" in data:
                        return data["translatedText"]
                    else:
                        log.warning(f"API Error: 'translatedText' not in response: {data}")
                        raise ValueError("Malformed JSON response from API")
                except json.JSONDecodeError:
                    log.error(f"API Error: Failed to decode JSON on attempt {attempt + 1}.")
                    log.debug(f"Raw response content: {response.text[:500]}")
                    raise requests.exceptions.RequestException("JSONDecodeError")

            except requests.exceptions.RequestException as e:
                log.warning(f"API request failed on attempt {attempt + 1}/{self.retries}: {e}")
                if attempt < self.retries - 1:
                    sleep_time = self.backoff_factor * (2 ** attempt)
                    log.info(f"Retrying in {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                else:
                    log.error("API translation failed after multiple retries.")
                    return None
        return None

    def load_glossary(self, glossary_path: str):
        """Glossary is not supported for this simple API backend."""
        log.info("Glossary not supported for this API backend.")
        pass