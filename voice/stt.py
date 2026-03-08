"""Speech-to-Text — local transcription using faster-whisper (tiny model)."""

import logging
import io
import tempfile
import time
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 500       # RMS amplitude below which = silence
SILENCE_DURATION = 1.5        # seconds of silence to end recording
MAX_RECORD_SECONDS = 15       # hard cap on recording length
CHANNELS = 1


class SpeechToText:
    """Records audio after wake word and transcribes locally with faster-whisper."""

    def __init__(self, model_size: str = "tiny", device: str = "cpu", compute_type: str = "int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _load_model(self):
        """Lazy-load the Whisper model."""
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            logger.info(f"Whisper model loaded: {self.model_size} ({self.device}/{self.compute_type})")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def record_until_silence(self) -> Optional[np.ndarray]:
        """Record audio from mic until silence is detected. Returns numpy int16 array."""
        import sounddevice as sd

        logger.info("Recording speech...")
        frames = []
        silence_start = None
        start_time = time.time()

        def callback(indata, frame_count, time_info, status):
            nonlocal silence_start
            if status:
                logger.warning(f"Recording status: {status}")
            audio = np.frombuffer(indata, dtype=np.int16).copy()
            frames.append(audio)
            rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
            if rms < SILENCE_THRESHOLD:
                if silence_start is None:
                    silence_start = time.time()
            else:
                silence_start = None

        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=1024,
            dtype="int16",
            channels=CHANNELS,
            callback=callback,
        ):
            while True:
                time.sleep(0.05)
                elapsed = time.time() - start_time
                if elapsed > MAX_RECORD_SECONDS:
                    logger.info("Max recording time reached")
                    break
                if silence_start and (time.time() - silence_start) > SILENCE_DURATION:
                    logger.info("Silence detected — stopping recording")
                    break

        if not frames:
            return None

        audio = np.concatenate(frames)
        duration = len(audio) / SAMPLE_RATE
        logger.info(f"Recorded {duration:.1f}s of audio")
        return audio

    def transcribe(self, audio: np.ndarray) -> str:
        """Transcribe a numpy int16 audio array to text."""
        self._load_model()
        # faster-whisper expects float32 normalized to [-1, 1]
        audio_f32 = audio.astype(np.float32) / 32768.0

        segments, info = self._model.transcribe(
            audio_f32,
            beam_size=1,
            language="en",
            vad_filter=True,
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        logger.info(f"Transcribed: '{text}' (lang={info.language}, prob={info.language_probability:.2f})")
        return text

    def listen_and_transcribe(self) -> str:
        """Full pipeline: record until silence, then transcribe."""
        audio = self.record_until_silence()
        if audio is None or len(audio) < SAMPLE_RATE * 0.3:  # < 0.3s = noise
            return ""
        return self.transcribe(audio)
