# OpenSpec: Yale door unlock / auto-lock behavior

- Date: 2026-10-18
- Area: Home Assistant / Yale lock
- Status: implemented

## Summary

This change updates the Yale door logic so that the entrance light turns on immediately when the main door is unlocked, the auto-lock timer is restarted at unlock time, and the auto-lock only executes when the door is already closed.

## Problem

The previous logic only started the lock timer when the door closed. There was no automatic action when the lock changed to unlocked, so the entrance light did not come on in the expected moment. The auto-lock also depended on the timer finishing without checking whether the door was still open.

## Scope

- Active Home Assistant package: myPackages/yale/cerradura.yaml
- Effected behavior: unlock event, entry light activation, timer-based auto-lock, log messages

## Files changed

- myPackages/yale/cerradura.yaml

## Decision and implementation

- Added a trigger on lock.puerta_principal_2 changing to unlocked.
- Restarted timer.bloqueo_puerta_principal when the door is unlocked.
- Added a light.turn_on action for light.columna_led_entrada with instant transition.
- Kept the auto-lock only when BOTH conditions are true:
  - lock.puerta_principal_2 is unlocked
  - binary_sensor.puerta_principal_door_2 is off
- Added a warning log when the timer expires while the door is still open, so the lock is not forced closed in a false state.

## Verification

The updated YAML was validated with a Python parser:

- OK automations: 4
- OK scripts: ['abrir_puerta_principal', 'cerrar_puerta_principal', 'desbloquear_puerta_principal']

## Risks and rollback

- Risk: the lock may remain unlocked longer if the door is not closed before the timer expires; this is intentional to avoid locking an open door.
- Rollback: revert the automation section in myPackages/yale/cerradura.yaml to the previous version if behavior needs to be reverted.

## Notes

This behavior is designed to match the expected user flow: unlock door -> light on -> auto-lock only after the door is closed.
