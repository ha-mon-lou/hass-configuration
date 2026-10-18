# OpenSpec: Renombrar el script de notificación móvil

- Date: 2026-10-18
- Area: Home Assistant / scripts and automations
- Status: implemented; runtime validation pending

## Summary

Renamed the `notifica_movil` script to `notificacion_movil` and updated its active automation references.

## Problem / Trigger

Home Assistant reported `script.notifica_movil` as an unknown action in the "Secuencia de apagado" automation, despite the script YAML, include configuration, and entity registry showing the old script ID. Renaming the script is a diagnostic attempt to make Home Assistant load and register it under a fresh ID.

## Scope

- Active script definition in `myScripts`
- Active references in shutdown and lighting-timer automations
- No changes to `_sandbox` or Home Assistant's `.storage` registry

## Files changed

- `myScripts/notifica_movil.yaml` (renamed to `myScripts/notificacion_movil.yaml`)
- `myAutomation/shutdown/secuencia.yaml`
- `myAutomation/timer/temporizador_luces.yaml`
- `AGENTS.md`

## Decision / implementation

- Changed the script key and filename to `notificacion_movil`.
- Updated both calls in the shutdown sequence and the call in the lighting-timer automation to `script.notificacion_movil`.
- Left experimental `_sandbox` references unchanged because those files are not loaded as active configuration.

## Verification

- YAML parsing succeeded for all three changed configuration files.
- Searched active configuration directories: no remaining `script.notifica_movil` references or old script key were found.
- `ha core check` completed successfully.
- The script reload or Home Assistant restart has not yet been performed, so runtime entity registration and automation execution remain to be verified.

## Risks / rollback

- The rename alone may not resolve the original error if its cause is a stale or failed runtime reload.
- After reloading scripts or restarting Home Assistant, confirm `script.notificacion_movil` exists and test the affected automation.
- To roll back, restore the original filename/key and all three automation references to `notifica_movil`.
