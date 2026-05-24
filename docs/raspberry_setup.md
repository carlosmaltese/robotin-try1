# Robotin Raspberry Pi Setup

This document describes the dual GC9A01 round SPI screens for Task 012 and Task 013.

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

## Task 013: independent CS/DC/RST per eye

Task 013 updates the pin model so each eye display uses independent control pins:

- Left eye: independent `CS`, `DC`, `RST`
- Right eye: independent `CS`, `DC`, `RST`
- Shared between both eyes: `VCC`, `GND`, `MOSI`, `SCLK`

Updated pin fields used by `GC9A01DisplayPins`:

- `left_cs_pin`, `left_dc_pin`, `left_rst_pin`
- `right_cs_pin`, `right_dc_pin`, `right_rst_pin`

## Visual states

Supported visual states for the eyes renderer:

- `idle`
- `listening`
- `thinking`
- `speaking`
- `sleeping` (demo-only)
- `error`

Each physical display renders **one eye** (left or right) with an eyebrow.
The dual setup therefore shows a full face expression across both round screens.

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

The prototype uses shared SPI data/clock and independent per-eye CS/DC/RST.

### Shared wiring

- VCC
- GND
- SDA / MOSI
- SCL / SCLK

### Per-eye control wiring (Task 013)

| Eye | Signal | Physical pin | GPIO |
|---|---|---:|---:|
| Left | CS | 24 | GPIO8 |
| Left | DC | 22 | GPIO25 |
| Left | RST | 18 | GPIO24 |
| Right | CS | 26 | GPIO7 |
| Right | DC | 16 | GPIO23 |
| Right | RST | 15 | GPIO22 |

Optional backlight in demo script:

- BL: GPIO18

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
pip install adafruit-blinka adafruit-circuitpython-rgb-display
```

The current adapter uses `adafruit_rgb_display.gc9a01a`.

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
