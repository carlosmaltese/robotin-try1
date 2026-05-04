# Robotin Protocol Notes

This document will describe communication protocols used by Robotin.

Initial phase:

- No real hardware protocol is implemented.
- No real AI protocol is required.
- Mock adapters are used first.

## Future AI client protocol

Robotin may communicate with a local AI backend over HTTP.

The final protocol is not decided yet.

Initial likely request shape:

```json
{
  "input": "Hello Robotin",
  "context": {
    "robot_state": "listening"
  }
}
```

Initial likely response shape:

```json
{
  "text": "Hello! I am Robotin."
}
```

This is only a draft and should not be treated as implemented until the corresponding task exists.

## Future STT protocol

Robotin may communicate with a local STT service.

Possible approaches:

- send recorded audio file,
- send audio chunks,
- receive transcribed text.

This should be defined later after the basic robot brain is working.

## Future hardware protocol

If Robotin later uses a microcontroller for motors, LEDs, or sensors, communication may use:

- serial,
- USB,
- UART,
- I2C,
- MQTT,
- another simple local protocol.

Any hardware protocol must include:

- clear command names,
- validation,
- safe defaults,
- timeouts,
- error handling,
- manual test procedures.

## Safety requirements for protocols

Every protocol involving external systems must include:

- explicit timeout behavior,
- clear error handling,
- deterministic tests where possible,
- safe fallback behavior,
- no internet dependency for normal runtime.
