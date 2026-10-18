# OpenSpec: Floorplan Pinguino fan animation

- Date: 2026-10-18
- Area: Home Assistant / Floorplan SVG
- Status: experimental, not active

## Context

The active dashboard uses `switch.alias_pinguino` as the target for `image_set` and the `spinning` class. Its SVG group has a static transform that positions and scales it on the floorplan.

## Problem

When the entity turns on, the spinning animation applies CSS `transform` to the same SVG group that carries the placement transform. The CSS animation can override that transform and move the fan away from its intended position.

## Change made

Created an isolated SVG variant. The placement matrix is now on an outer wrapper, while the inner `switch.alias_pinguino` group keeps its ID and graphic paths but no longer has a transform. This allows the animation to rotate the target group without replacing its placement matrix.

## Files touched

- `www/floorplan/canpallars/canpallar-261018a.svg` (new experimental variant)

## Validation

- XML parser accepted the SVG.
- Confirmed the placement matrix is on the outer wrapper.
- Confirmed the inner target ID and its two paths are preserved.
- The live dashboard still points to `canpallars-260214c.svg`; no runtime behavior has been changed or visually tested.

## Notes / next steps

To test this variant in Home Assistant, temporarily point a test dashboard at it and verify the fan remains in place while spinning. Rollback is simply to keep using the original SVG; it was not modified.
