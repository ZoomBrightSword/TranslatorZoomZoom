import ctranslate2
import os
import json
import re
from pathlib import Path
from transformers import AutoTokenizer
from ...utils.logger import log

# Define paths for the local model
MODEL_DIR = Path.home() / ".GameTranslator" / "models" / "enid_ctranslate2"
HF_MODEL_NAME = "Helsinki-NLP/opus-mt-en-id"

class LocalTranslator:
    """
    A translation backend that uses a local CTranslate2 model.
    """
    def __init__(self, model_path: str = str(MODEL_DIR)):
        self.model_path = model_path
        self.translator = None
        self.tokenizer = None
        self.glossary = {}
        self.case_sensitive = False
        self._load_model_and_tokenizer()

    def _load_model_and_tokenizer(self):
        """Loads the CTranslate2 model and the Hugging Face tokenizer."""
        try:
            self.translator = ctranslate2.Translator(self.model_path, device="cpu")
            self.tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)
            log.info("Local CTranslate2 model and tokenizer loaded successfully.")
        except Exception as e:
            log.error(f"Failed to load local model or tokenizer: {e}")
            self.translator = None
            self.tokenizer = None

    def load_glossary(self, glossary_path: str):
        """
        Loads the glossary directly for post-translation replacement.
        """
        try:
            with open(glossary_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.glossary = data.get("terms", {})
                settings = data.get("settings", {})
                self.case_sensitive = settings.get("case_sensitive", False)
                log.info("Glossary loaded for local translator.")
        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Could not load or parse glossary file: {e}")
            self.glossary = {}

    def _apply_glossary(self, text: str) -> str:
        """
        Applies glossary replacements to the already translated text.
        """
        if not self.glossary:
            return text

        for source_term, target_term in self.glossary.items():
            if self.case_sensitive:
                text = text.replace(source_term, target_term)
            else:
                pattern = re.compile(re.escape(source_term), re.IGNORECASE)
                text = pattern.sub(target_term, text)
        return text

    def translate(self, text: str) -> str | None:
        """
        Translates a string of text from English to Indonesian.
        """
        if not self.translator or not self.tokenizer or not text:
            return None

        try:
            source_tokens = self.tokenizer.tokenize(text)
            results = self.translator.translate_batch(
                [source_tokens],
                repetition_penalty=1.2
            )
            target_tokens = results[0].hypotheses[0]
            translated_text = self.tokenizer.decode(
                self.tokenizer.convert_tokens_to_ids(target_tokens),
                skip_special_tokens=True
            )
            final_text = self._apply_glossary(translated_text)
            return final_text
        except Exception as e:
            log.error(f"Error during local translation: {e}")
            return None