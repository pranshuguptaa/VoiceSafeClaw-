"""Wake Word Detection — continuous listening for 'Hey Jarvis' using openWakeWord."""

import logging
import threading
import time
from typing import Callable, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Audio config
SAMPLE_RATE = 16000
CHUNK_SAMPLES = 1280  # 80ms frames for openWakeWord
CHANNELS = 1


class WakeWordDetector:
    """Listens for a wake word using openWakeWord (fully local)."""

    def __init__(
        self,
        wake_word: str = "hey_jarvis",
        threshold: float = 0.5,
        on_wake: Optional[Callable[[], None]] = None,
    ):
        self.wake_word = wake_word
        self.threshold = threshold
        self.on_wake = on_wake
        self._running = False
        self._model = None
        self._stream = None

    def _load_model(self):
        """Load the openWakeWord model."""
        try:
            import openwakeword
            from openwakeword.model import Model
            openwakeword.utils.download_models()
            self._model = Model(wakeword_models=[self.wake_word])
            logger.info(f"Wake word model loaded: {self.wake_word}")
        except Exception as e:
            logger.error(f"Failed to load wake word model: {e}")
            raise

    def _audio_callback(self, indata, frames, time_info, status):
        """PyAudio/sounddevice callback — feed audio to wake model."""
        if status:
            logger.warning(f"Audio status: {status}")
        if not self._running or self._model is None:
            return

        audio = np.frombuffer(indata, dtype=np.int16)
        prediction = self._model.predict(audio)

        for model_name, score in prediction.items():
            if score >= self.threshold:
                logger.info(f"Wake word detected! ({model_name}: {score:.3f})")
                self._model.reset()
                if self.on_wake:
                    self.on_wake()

    def start(self):
        """Start listening for the wake word."""
        if self._running:
            return
        self._load_model()
        self._running = True

        try:
            import sounddevice as sd
            self._stream = sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=CHUNK_SAMPLES,
                dtype="int16",
                channels=CHANNELS,
                callback=self._audio_callback,
            )
            self._stream.start()
            logger.info("Wake word detector started")
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            self._running = False
            raise

    def stop(self):
        """Stop listening."""
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        logger.info("Wake word detector stopped")

    @property
    def is_listening(self) -> bool:
        return self._running
