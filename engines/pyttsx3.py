"""
pyttsx3 TTS Engine

Offline text-to-speech using espeak backend.
"""

from libs.exceptions import EngineNotAvailableError, TTSException
import os
import tempfile
import time
import logging
import sys
from pathlib import Path as PathLib

# Add libs to path
sys.path.insert(0, str(PathLib(__file__).parent.parent / "libs"))

logger = logging.getLogger(__name__)

# Try to import pyttsx3
try:
    import pyttsx3  # type: ignore

    AVAILABLE = True
except ImportError:
    AVAILABLE = False
    logger.warning("pyttsx3 not available. Install with: pip install pyttsx3")


def is_available() -> bool:
    """Check if pyttsx3 is available."""
    return AVAILABLE


def generate(
    text: str,
    language: str = "id",
    voice: str = None,
    rate: int = 150,
    volume: float = 0.9,
    output_format: str = "wav",
    output_path: str = None,
    **kwargs,
) -> bytes:
    """
    Generate speech using pyttsx3 (offline)
    Args:
        text: Text to synthesize
        language: language code (e.g. 'id', 'en')
        voice: voice id (optional)
        rate: speaking rate
        volume: volume (0.0 - 1.0)
    Returns:
        Audio bytes in WAV format
    """
    import pyttsx3

    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)

    voices = engine.getProperty("voices")
    if voice:
        # Manual override jika user tentukan voice
        engine.setProperty("voice", voice)
    elif voices:
        # Kalau tidak ada preferensi, gunakan voice pertama
        engine.setProperty("voice", voices[0].id)
        # Coba cari voice yang cocok dengan bahasa
        for v in voices:
            if hasattr(v, "languages"):
                langs = [str(l).lower() for l in v.languages]
                if language in langs or f"{language}_" in "".join(langs):
                    engine.setProperty("voice", v.id)
                    break
                elif language == "id" and ("indonesian" in v.name.lower() or "id" in v.id.lower()):
                    engine.setProperty("voice", v.id)
                    break

    if not AVAILABLE:
        raise EngineNotAvailableError("pyttsx3 not available")

    try:

        # Generate to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            engine.save_to_file(text, temp_filename)
            engine.runAndWait()

            # Give time for file writing (Linux espeak issue)
            time.sleep(0.5)
            engine.stop()

            # Read and return bytes
            if not os.path.exists(temp_filename) or os.path.getsize(temp_filename) == 0:
                raise TTSException("pyttsx3 failed to generate audio")

            with open(temp_filename, "rb") as f:
                return f.read()
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    except Exception as e:
        raise TTSException(f"pyttsx3 generation failed: {e}")