# OpenSpec: Fan turn-off from Floorplan controls

- Date: 2026-10-18
- Area: Home Assistant / Ventilation scripts
- Status: implemented

## Context

The Floorplan controls toggle `input_boolean.ventilador_habitacion` and `input_boolean.ventilador_despacho`. Their off automations call the shared `script.selector_ventilador` with the `Apagar` option.

## Problem

The helper boolean changes to `off` before the off automation calls the selector. The selector then skipped the Broadlink command whenever the requested option was `Apagar` and the helper was already off, so the UI state changed but the physical fan did not receive the off command.

## Change made

Removed the helper-state guard around `script.envia_comando_broadlink`. The selector already exits without sending a command when the selected option is unchanged; when the option changes, it now sends the requested command, including `Apagar`.

## Files touched

- `myScripts/ventiladores/selector_ventilador.yaml`

## Validation

- Parsed the selector YAML successfully.
- Confirmed both room and office off automations route through `script.selector_ventilador`.
- Confirmed the Broadlink call remains in the selector branch that executes when the selected option changes.
- User confirmed both fans now turn on and off correctly after a full Home Assistant restart.

## Risks and rollback

- A fan whose selector is inconsistent with its boolean may receive an additional `Apagar` command when the selector changes to `Apagar`; this is intentional to synchronize the physical device. If this causes an issue, restore the prior conditional around the Broadlink call.

## Notes

The initial full configuration reload failed with `Errno 24` while opening `automations.yaml`; after a full Home Assistant restart, the user confirmed both Floorplan fan controls work.
