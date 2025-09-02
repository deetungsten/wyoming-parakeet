# Wyoming Parakeet

[Wyoming protocol](https://github.com/rhasspy/wyoming) server for the [Parakeet](https://github.com/NVIDIA/NeMo) speech to text system.

## Home Assistant Add-on

[![Show add-on](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?addon=core_whisper)

[Source](https://github.com/home-assistant/addons/tree/master/whisper)

## Local Install

Clone the repository and set up Python virtual environment:

``` sh
git clone https://github.com/rhasspy/wyoming-parakeet.git
cd wyoming-parakeet
script/setup
```

Run a server anyone can connect to:

```sh
script/run --model nvidia/parakeet-tdt-1.1b --language en --uri 'tcp://0.0.0.0:10300' --data-dir /data --download-dir /data
```

The `--model` can also be other Parakeet models like `nvidia/parakeet-tdt-0.6b`

## Docker Image

``` sh
docker run -it -p 10300:10300 -v /path/to/local/data:/data rhasspy/wyoming-parakeet \
    --model nvidia/parakeet-tdt-1.1b --language en
```

**NOTE**: Models are downloaded temporarily to the `HF_HUB_CACHE` directory, which defaults to `~/.cache/huggingface/hub`.
You may need to adjust this environment variable when using a read-only root filesystem (e.g., `HF_HUB_CACHE=/tmp`).

## Jetson Orin Nano Deployment

For NVIDIA Jetson Orin Nano devices, use the optimized Docker configuration:

### Prerequisites

1. Install Docker and docker-compose on your Jetson device
2. Install NVIDIA Container Runtime:
   ```bash
   sudo apt-get update
   sudo apt-get install nvidia-docker2
   sudo systemctl restart docker
   ```

### Quick Start

1. Clone and build:
   ```bash
   git clone https://github.com/rhasspy/wyoming-parakeet.git
   cd wyoming-parakeet
   ./build-jetson.sh
   ```

2. Run with docker-compose:
   ```bash
   docker-compose -f docker-compose.jetson.yml up -d
   ```

3. Check logs:
   ```bash
   docker-compose -f docker-compose.jetson.yml logs -f
   ```

### Configuration

The Jetson deployment uses optimized settings:
- Model: `nvidia/parakeet-tdt-0.6b` (smaller model for better performance)
- Precision: `float16` (reduced memory usage)
- Memory limit: 6GB
- GPU acceleration enabled

### Custom Model

To use a different Parakeet model, set the environment variable:
```bash
MODEL_NAME=nvidia/parakeet-tdt-1.1b docker-compose -f docker-compose.jetson.yml up -d
```

[Source](https://github.com/rhasspy/wyoming-addons/tree/master/whisper)
