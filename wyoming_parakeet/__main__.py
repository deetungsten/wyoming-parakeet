#!/usr/bin/env python3
import argparse
import asyncio
import logging
import platform
import re
from functools import partial
from typing import Any

import nemo.collections.asr as nemo_asr
from wyoming.info import AsrModel, AsrProgram, Attribution, Info
from wyoming.server import AsyncServer

from . import __version__
from .handler import ParakeetEventHandler

_LOGGER = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        required=True,
        help="Name of parakeet model to use (or auto)",
    )
    parser.add_argument("--uri", required=True, help="unix:// or tcp://")
    parser.add_argument(
        "--data-dir",
        required=True,
        action="append",
        help="Data directory to check for downloaded models",
    )
    parser.add_argument(
        "--download-dir",
        help="Directory to download models into (default: first data dir)",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Device to use for inference (default: cpu)",
    )
    parser.add_argument(
        "--language",
        help="Default language to set for transcription",
    )
    parser.add_argument(
        "--precision",
        default="float32",
        help="Model precision (float32, float16, bfloat16)",
    )
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Don't check HuggingFace hub for updates every time",
    )
    #
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    parser.add_argument(
        "--log-format", default=logging.BASIC_FORMAT, help="Format for log messages"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print version and exit",
    )
    args = parser.parse_args()

    if not args.download_dir:
        # Download to first data dir by default
        args.download_dir = args.data_dir[0]

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO, format=args.log_format
    )
    _LOGGER.debug(args)

    # Automatic configuration for ARM
    machine = platform.machine().lower()
    is_arm = ("arm" in machine) or ("aarch" in machine)

    # Set default parakeet model
    model_name = args.model
    if args.model == "auto":
        args.model = "nvidia/parakeet-tdt-1.1b"
        model_name = "parakeet-tdt-1.1b"

    if args.language == "auto":
        # Default to English for Parakeet
        args.language = "en"

    wyoming_info = Info(
        asr=[
            AsrProgram(
                name="parakeet",
                description="Parakeet transcription with NVIDIA NeMo",
                attribution=Attribution(
                    name="NVIDIA",
                    url="https://github.com/NVIDIA/NeMo",
                ),
                installed=True,
                version=__version__,
                models=[
                    AsrModel(
                        name=model_name,
                        description=model_name,
                        attribution=Attribution(
                            name="NVIDIA",
                            url="https://huggingface.co/nvidia",
                        ),
                        installed=True,
                        languages=["en"],
                        version="1.1b",
                    )
                ],
            )
        ],
    )

    # Load model
    _LOGGER.debug("Loading %s", args.model)
    parakeet_model: Any = None

    # Load Parakeet model using NeMo
    parakeet_model = nemo_asr.models.ASRModel.from_pretrained(
        args.model,
        map_location=args.device if args.device != "cpu" else "cpu"
    )

    server = AsyncServer.from_uri(args.uri)
    _LOGGER.info("Ready")
    model_lock = asyncio.Lock()

    # Use Parakeet model
    await server.run(
        partial(
            ParakeetEventHandler,
            wyoming_info,
            args,
            parakeet_model,
            model_lock,
        )
    )


# -----------------------------------------------------------------------------


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
