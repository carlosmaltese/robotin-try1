# Robotin Raspberry Pi Setup

This document describes the **Task 012** display prototype for dual GC9A01 round SPI screens.

Scope in this document:

- Dual-eye display wiring prototype.
- Raspberry Pi package setup for the demo.
- How to run the standalone display demo.

Out of scope:

- Runtime integration in `create_runtime()`.
- Audio setup.
- Wake word setup.
- ESP32 integration.

## Target device

Initial target:

- Raspberry Pi 4 with 8 GB RAM
- Raspberry Pi OS Lite 64-bit

Future target:

- Raspberry Pi 5

## Migration principle

The same logical architecture must work on:

```text
Windows development environment
Raspberry Pi 4
Raspberry Pi 5
```

Migration should mainly require infrastructure adapter changes, not domain or application rewrites.

## Task 012: dual GC9A01 prototype

Implemented files:

- `src/robotin/infrastructure/eyes_renderer.py`
- `src/robotin/infrastructure/display_gc9a01.py`
- `scripts/demo_eyes_gc9a01.py`

Key design points:

- Display rendering is Pillow-based and infrastructure-only.
- Robot states are mapped to visual states inside the adapter.
- Hardware-specific modules are imported lazily to keep Windows tests working.
- Main/runtime composition is intentionally unchanged in this task.

## Visual states

Supported visual states for the eyes renderer:

- `idle`
- `listening`
- `thinking`
- `speaking`
- `sleeping` (demo-only)
- `error`

Application mapping used by the display adapter:

- `RobotState.IDLE -> idle`
- `RobotState.LISTENING -> listening`
- `RobotState.PROCESSING -> thinking`
- `RobotState.SPEAKING -> speaking`
- `RobotState.ERROR -> error`

## Hardware bill of materials

- Raspberry Pi 4 (8 GB recommended) or Raspberry Pi 5.
- 2x round 1.28" TFT displays with GC9A01 controller (240x240).
- Jumper wires.
- Common 3.3V and GND wiring.

## Wiring reference (prototype)

The prototype assumes shared SPI clock/MOSI and separate CS lines.

Configured pins in `scripts/demo_eyes_gc9a01.py`:

- DC: GPIO25
- RST: GPIO24
- Left display CS: GPIO8 (CE0)
- Right display CS: GPIO7 (CE1)
- Backlight (optional): GPIO18

Shared SPI lines:

- SCLK from Pi SPI clock pin
- MOSI from Pi SPI MOSI pin

Power:

- Display VCC -> 3.3V
- Display GND -> GND

Notes:

- Keep both displays on the same SPI bus clock and MOSI.
- Each display must have its own CS pin.
- Use short, stable wiring to reduce noise at higher SPI rates.

## Raspberry Pi OS setup

1. Install Raspberry Pi OS Lite 64-bit.
2. Enable SPI:
   - `sudo raspi-config`
   - Interface Options -> SPI -> Enable
3. Reboot.

## Python environment setup

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Install Raspberry Pi display dependencies (example set):

```bash
pip install adafruit-blinka adafruit-circuitpython-gc9a01
```

If your GC9A01 board uses a different Python driver package, adjust accordingly.

## Run the standalone dual-eye demo

From project root on Raspberry Pi:

```bash
python scripts/demo_eyes_gc9a01.py
```

The demo cycles through:

- idle
- listening
- thinking
- speaking
- sleeping
- error

Use `Ctrl+C` to stop.

## Future setup topics

This document will eventually include:

- Raspberry Pi OS installation notes,
- Python installation,
- virtual environment setup,
- audio device configuration,
- display configuration,
- local AI backend configuration,
- Piper TTS setup,
- openWakeWord setup,
- `systemd` service setup,
- logging,
- safe shutdown,
- startup scripts.

## Initial phase rule

During the initial phase:

- do not require Raspberry Pi hardware,
- do not require GPIO,
- do not require microphone hardware,
- do not require speaker hardware,
- do not require a real display,
- use mocks instead.

## Future systemd service

A future service may look conceptually like this:

```text
robotin.service
```

But it should not be added until the application has a stable entry point and configuration model.

## Hardware adapter rule

Raspberry Pi-specific code must live under:

```text
src/robotin/infrastructure/
```

Examples:

```text
display_raspberry.py
tts_piper.py
wake_word_openwakeword.py
microphone_sounddevice.py
```

Domain and application layers must remain portable.
