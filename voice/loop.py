"""Voice Loop Orchestrator — wake → record → STT → dispatch → TTS."""

import logging
import threading
import time
from typing import Optional, TYPE_CHECKING

from voice.wake import WakeWordDetector
from voice.stt import SpeechToText
from voice.tts import TextToSpeech

if TYPE_CHECKING:
    from core.engine import VoiceSafeClawEngine

logger = logging.getLogger(__name__)


class VoiceLoop:
    """Main voice loop: continuously listens for wake word, processes commands."""

    def __init__(
        self,
        engine: "VoiceSafeClawEngine",
        wake_word: str = "hey_jarvis",
        wake_threshold: float = 0.5,
        stt_model: str = "tiny",
        tts_engine: str = "piper",
        tts_voice: Optional[str] = None,
    ):
        self.engine = engine
        self._running = False
        self._processing = False

        # Load config from env with param defaults
        import os
        wake_word = os.environ.get("WAKE_WORD", wake_word)
        stt_model = os.environ.get("STT_MODEL", stt_model)
        tts_engine = os.environ.get("TTS_ENGINE", tts_engine)

        self.stt = SpeechToText(model_size=stt_model)
        self.tts = TextToSpeech(engine=tts_engine, voice=tts_voice)
        self.wake_detector = WakeWordDetector(
            wake_word=wake_word,
            threshold=wake_threshold,
            on_wake=self._on_wake,
        )

    def _on_wake(self):
        """Called when wake word is detected."""
        if self._processing:
            return  # Ignore re-triggers while processing
        self._processing = True
        logger.info("Wake word detected — starting command pipeline")
        threading.Thread(target=self._process_command, daemon=True).start()

    def _process_command(self):
        """Full pipeline: chime → record → STT → dispatch → TTS."""
        try:
            # Play a subtle chime/beep to indicate listening
            self._play_listening_indicator()

            # Record and transcribe
            text = self.stt.listen_and_transcribe()
            if not text:
                logger.info("No speech detected after wake word")
                self.tts.speak("Sorry, I didn't catch that.")
                return

            logger.info(f"User said: '{text}'")

            # Dispatch through engine
            response = self.engine.process_command(text)

            # Speak the response
            if response:
                self.tts.speak(response)

        except Exception as e:
            logger.exception("Error processing voice command")
            self.tts.speak("Sorry, something went wrong.")
        finally:
            self._processing = False

    def _play_listening_indicator(self):
        """Play a brief tone to indicate the assistant is listening."""
        try:
            import sounddevice as sd
            import numpy as np
            duration = 0.15  # seconds
            freq = 880  # Hz (A5)
            t = np.linspace(0, duration, int(22050 * duration), endpoint=False)
            tone = (np.sin(2 * np.pi * freq * t) * 0.3).astype(np.float32)
            # Fade in/out to avoid clicks
            fade = int(22050 * 0.02)
            tone[:fade] *= np.linspace(0, 1, fade).astype(np.float32)
            tone[-fade:] *= np.linspace(1, 0, fade).astype(np.float32)
            sd.play(tone, 22050)
            sd.wait()
        except Exception:
            pass  # Non-critical

    def run(self):
        """Start the voice loop (blocking)."""
        self._running = True
        logger.info("Voice loop starting...")

        try:
            self.wake_detector.start()
            logger.info("Voice loop is active — listening for wake word")
            while self._running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        """Stop the voice loop."""
        self._running = False
        self.wake_detector.stop()
        logger.info("Voice loop stopped")

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_processing(self) -> bool:
        return self._processing
