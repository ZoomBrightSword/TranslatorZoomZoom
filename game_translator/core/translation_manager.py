from .translation_backends.local_translator import LocalTranslator
from .translation_backends.api_translator import ApiTranslator
from ..config import config_manager
from ..utils.logger import log

class TranslationManager:
    """
    Manages and routes translation requests to the configured backend.
    This acts as a factory and a router for different translation services.
    """
    def __init__(self):
        """
        Initializes the TranslationManager by selecting and loading the
        appropriate backend based on the application's configuration.
        """
        self.backend = None
        self._select_backend()

    def _select_backend(self):
        """
        Selects the translation backend based on the config file.
        Defaults to 'local' if the setting is not found.
        """
        backend_name = config_manager.get("translation_backend", "local")
        log.info(f"Selected translation backend: {backend_name}")

        if backend_name == "api":
            self.backend = ApiTranslator()
        elif backend_name == "local":
            self.backend = LocalTranslator()
        else:
            log.warning(f"Unknown backend '{backend_name}'. Defaulting to 'local'.")
            self.backend = LocalTranslator()

    def load_glossary(self, glossary_path: str):
        """
        Loads the glossary using the active backend.
        """
        if self.backend:
            self.backend.load_glossary(glossary_path)

    def translate(self, text: str) -> str | None:
        """
        Routes the translation request to the active backend.
        """
        if self.backend:
            return self.backend.translate(text)
        else:
            log.error("No translation backend is active.")
            return None