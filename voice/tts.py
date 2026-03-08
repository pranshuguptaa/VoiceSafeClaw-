"""Text-to-Speech — local speech synthesis using piper-tts or kokoro-onnx."""

import logging
import os
import tempfile
import wave
import subprocess
import sys
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

SAMPLE_RATE = 22050


class TextToSpeech:
    """Speaks text aloud using a local TTS engine (piper or kokoro)."""

    def __init__(self, engine: str = "piper", voice: Optional[str] = None):
        self.engine = engine.lower()
        self.voice = voice
        self._piper_voice = None

    def _init_piper(self):
        """Initialize piper-tts voice."""
        if self._piper_voice is not None:
            return
        try:
            from piper import PiperVoice
            voice_path = self.voice
            if not voice_path:
                # Use default bundled voice
                import piper
                models_dir = os.path.join(os.path.dirname(piper.__file__), "voices")
                if os.path.isdir(models_dir):
                    voices = [f for f in os.listdir(models_dir) if f.endswith(".onnx")]
                    if voices:
                        voice_path = os.path.join(models_dir, voices[0])

            if voice_path and os.path.exists(voice_path):
                self._piper_voice = PiperVoice.load(voice_path)
                logger.info(f"Piper voice loaded: {voice_path}")
            else:
                logger.warning("No piper voice model found — using fallback system TTS")
        except ImportError:
            logger.warning("piper-tts not installed — using fallback system TTS")

    def _speak_piper(self, text: str):
        """Synthesize and play audio with piper-tts."""
        self._init_piper()
        if self._piper_voice is None:
            self._speak_fallback(text)
            return

        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            with wave.open(tmp.name, "wb") as wf:
                self._piper_voice.synthesize(text, wf)
            self._play_wav(tmp.name)
        except Exception as e:
            logger.error(f"Piper TTS failed: {e}")
            self._speak_fallback(text)
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def _speak_kokoro(self, text: str):
        """Synthesize and play audio with kokoro-onnx."""
        try:
            from kokoro_onnx import Kokoro
            kokoro = Kokoro(self.voice) if self.voice else Kokoro()
            samples, sr = kokoro.create(text, voice="af_bella", speed=1.0)
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            with wave.open(tmp.name, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes((samples * 32767).astype(np.int16).tobytes())
            self._play_wav(tmp.name)
            os.unlink(tmp.name)
        except ImportError:
            logger.warning("kokoro-onnx not installed — using fallback")
            self._speak_fallback(text)
        except Exception as e:
            logger.error(f"Kokoro TTS failed: {e}")
            self._speak_fallback(text)

    def _speak_fallback(self, text: str):
        """Fallback: use macOS `say` or Windows SAPI."""
        try:
            if sys.platform == "darwin":
                subprocess.run(["say", text], check=True)
            elif sys.platform == "win32":
                ps_cmd = f'Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak("{text}")'
                subprocess.run(["powershell", "-Command", ps_cmd], check=True)
            else:
                logger.warning(f"No TTS available — text: {text}")
        except Exception as e:
            logger.error(f"Fallback TTS failed: {e}")

    def _play_wav(self, path: str):
        """Play a WAV file using sounddevice."""
        try:
            import sounddevice as sd
            import soundfile as sf
            data, sr = sf.read(path, dtype="float32")
            sd.play(data, sr)
            sd.wait()
        except ImportError:
            # Fallback: use system player
            if sys.platform == "darwin":
                subprocess.run(["afplay", path])
            elif sys.platform == "win32":
                subprocess.run(["powershell", "-Command", f'(New-Object Media.SoundPlayer "{path}").PlaySync()'])

    def speak(self, text: str):
        """Speak the given text aloud."""
        if not text or not text.strip():
            return
        logger.info(f"TTS ({self.engine}): {text[:80]}...")
        if self.engine == "piper":
            self._speak_piper(text)
        elif self.engine == "kokoro":
            self._speak_kokoro(text)
        else:
            self._speak_fallback(text)
