"""Event handler for clients of the server."""
import argparse
import asyncio
import logging
import os
import tempfile
import wave
from typing import Optional, Any

import torch
import librosa
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler

_LOGGER = logging.getLogger(__name__)


class ParakeetEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        model: Any,
        model_lock: asyncio.Lock,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.model = model
        self.model_lock = model_lock
        self._language = self.cli_args.language
        self._wav_dir = tempfile.TemporaryDirectory()
        self._wav_path = os.path.join(self._wav_dir.name, "speech.wav")
        self._wav_file: Optional[wave.Wave_write] = None
        self._audio_data = []

    async def handle_event(self, event: Event) -> bool:
        if AudioChunk.is_type(event.type):
            chunk = AudioChunk.from_event(event)

            if self._wav_file is None:
                self._wav_file = wave.open(self._wav_path, "wb")
                self._wav_file.setframerate(chunk.rate)
                self._wav_file.setsampwidth(chunk.width)
                self._wav_file.setnchannels(chunk.channels)

            self._wav_file.writeframes(chunk.audio)
            return True

        if AudioStop.is_type(event.type):
            _LOGGER.debug("Audio stopped. Transcribing with Parakeet")
            assert self._wav_file is not None

            self._wav_file.close()
            self._wav_file = None

            async with self.model_lock:
                # Load audio using librosa
                audio_data, sample_rate = librosa.load(self._wav_path, sr=16000)
                
                # Convert to list for NeMo model
                audio_signal = [torch.tensor(audio_data)]
                audio_signal_length = [torch.tensor(len(audio_data))]
                
                # Transcribe with Parakeet model
                transcriptions = self.model.transcribe(
                    audio_signal=audio_signal,
                    audio_signal_length=audio_signal_length
                )
                
                # Extract text from transcription result
                text = transcriptions[0] if transcriptions else ""

            _LOGGER.info(text)

            await self.write_event(Transcript(text=text).event())
            _LOGGER.debug("Completed request")

            # Reset
            self._language = self.cli_args.language
            self._audio_data = []

            return False

        if Transcribe.is_type(event.type):
            transcribe = Transcribe.from_event(event)
            if transcribe.language:
                self._language = transcribe.language
                _LOGGER.debug("Language set to %s", transcribe.language)
            return True

        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        return True
