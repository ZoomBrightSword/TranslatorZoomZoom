from dataclasses import dataclass, field
from enum import Enum, auto

class PipelineStatus(Enum):
    """Represents the current status of the processing pipeline."""
    IDLE = auto()
    CAPTURING = auto()
    OCR = auto()
    TRANSLATING = auto()
    PAUSED = auto()
    ERROR = auto()

@dataclass
class PipelineResult:
    """
    A data structure to hold the complete result of a single pipeline run.
    """
    text: str = ""
    status: PipelineStatus = PipelineStatus.IDLE
    processing_time_ms: float = 0.0
    error_message: str | None = None

    def get_status_message(self) -> str:
        """Returns a user-friendly string for the current status."""
        status_map = {
            PipelineStatus.IDLE: "Menunggu perubahan...",
            PipelineStatus.CAPTURING: "Menangkap gambar...",
            PipelineStatus.OCR: "Mendeteksi teks (OCR)...",
            PipelineStatus.TRANSLATING: "Menerjemahkan...",
            PipelineStatus.PAUSED: "Dijeda",
            PipelineStatus.ERROR: f"Error: {self.error_message}",
        }
        return status_map.get(self.status, "Status tidak diketahui")