# Robotin Raspberry Pi Setup

This document is a placeholder for future Raspberry Pi setup instructions.

Do not implement Raspberry-specific setup during the initial phase unless explicitly requested.

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
