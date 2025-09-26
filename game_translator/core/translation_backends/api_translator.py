import requests
import time
import json

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
        print("API Translator (LibreTranslate) initialized.")

    def translate(self, text: str) -> str | None:
        if not text:
            return None

        payload = {"q": text, "source": "en", "target": "id", "format": "text"}

        for attempt in range(self.retries):
            try:
                response = requests.post(API_URL, json=payload, timeout=10)
                response.raise_for_status()  # Raise for 4xx/5xx status codes

                # Attempt to parse JSON, with specific error handling
                try:
                    data = response.json()
                    if "translatedText" in data:
                        return data["translatedText"]
                    else:
                        print(f"API Error: 'translatedText' not in response: {data}")
                        # Treat this as a failure and allow retry
                        raise ValueError("Malformed JSON response from API")
                except json.JSONDecodeError:
                    print(f"API Error: Failed to decode JSON on attempt {attempt + 1}.")
                    print(f"Raw response content:\n---\n{response.text[:500]}\n---")
                    # Raise an exception to trigger the retry mechanism
                    raise requests.exceptions.RequestException("JSONDecodeError")

            except requests.exceptions.RequestException as e:
                print(f"API request failed on attempt {attempt + 1}/{self.retries}: {e}")
                if attempt < self.retries - 1:
                    sleep_time = self.backoff_factor * (2 ** attempt)
                    print(f"Retrying in {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                else:
                    print("API translation failed after multiple retries.")
                    return None
        return None

    def load_glossary(self, glossary_path: str):
        """Glossary is not supported for this simple API backend."""
        print("Glossary not supported for this API backend.")
        pass