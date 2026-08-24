# What to print — Cerelog ESP-EEG V2 case

## Print these two. Nothing else.

| File | What it is |
|---|---|
| `case_v2_base.stl` | Bottom half. Walls, floor, 4 press-fit pegs, all port openings. |
| `case_v2_lid.stl`  | Top half. Engraving, LED holes, snap beads, 4 sleeves. |

Assembled size **102.60 x 46.55 x 11.35 mm**. No screws, no hardware.

## Orientation — read this before slicing

**Base:** floor flat on the bed, walls up. This is how it exports. No supports.

**Lid: FLIP IT 180 degrees.** The STL exports with the rim and sleeves pointing
*down* (STL spans Z 5.31..11.35). If you drop it straight onto the bed the
slicer balances it on four sleeves and prints the plate in mid-air.

Rotate 180 degrees about X so the **engraved top face lies on the bed** and the
rim and sleeves build upward. Then there are no overhangs anywhere and no
supports are needed.

Bonus: a **textured PEI sheet** puts a moulded-grain finish on the lid top,
which is the face you look at. That is the intended finish — the texture is
deliberately not in the geometry.

## Settings

- Nozzle 0.4, layer 0.2. Nothing here needs finer.
- **No supports on either part.**
- Walls are 1.60 mm (4 perimeters). Locally 0.60-0.80 mm at the switch,
  microSD and -X ports — do not let the slicer gap-fill those away.
- Two bridges in the base, over the microSD opening (17.4 mm) and the switch
  opening (9.0 mm). Slow that layer down.
- 3-4 perimeters, 20-30% infill. Material is not critical; PETG or ABS if the
  snap needs to survive repeated opening, PLA is fine otherwise.

## Assembly

1. Drop the PCB onto the four pegs in the base. It seats on the 2.50 mm
   shoulders; the pegs pass through the 2.20 mm mounting holes.
2. Press the lid on. The four sleeves swallow the protruding pegs, and three
   snap beads per long wall click into grooves in the base wall.
3. To open: pull from a short end. The snaps are 0.25 mm engagement, split
   into 14 mm segments so they release without tools.

## Before you print a second one

Three things are unresolved and would change the parts:

- **ON / OFF may be backwards.** The labels are placed from the switch
  actuator's position and travel axis. The STEP carries no electrical data, so
  nothing told me which throw actually powers the board. Meter it.
- **Two LED holes pierce the engraved title** (in `Cerelog` and `ESP-EEG V2`).
  Works fine, looks like damage. Fix is to move the title, not the holes.
- **The power switch actuator is a 1.30 x 1.16 mm nub** and sits roughly flush
  with the wall. No wall thickness fixes this; it needs a printed slider cap,
  which does not exist yet.

## Known-bad data in v2_step.step

Two 3D models in the KiCad export are wrong and were deliberately ignored:

- `530480210` battery connector — height is wrong.
- `SOLID`, `SOLID001`, `SOLID002` — unnamed, claim to hang 4.21 mm below the
  board. Confirmed not real.

If either turns out to be genuine, the case height and floor need revisiting.
