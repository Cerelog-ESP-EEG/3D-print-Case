# Cerelog ESP-EEG V2 — 3D printed case

Snap-fit two-part enclosure, **102.60 x 46.55 x 11.35 mm**. No screws.

**Printing? Go straight to [`stl/PRINT.md`](stl/PRINT.md).**

## Folders

| Folder | What lives there |
|---|---|
| **`stl/`** | The two printable STLs and `PRINT.md`. This is all you need at the printer. |
| **`Case files FreeCAD/`** | FreeCAD documents — the case on its own, the case with the board in it, and the original KiCad STEP export. |
| **`design/`** | The parametric source, measurements, build log, previews, and `tools/`. |

## How the design is built

The case is **not modelled by hand**. `design/case_v2.py` builds both parts from
named constants and exports the STLs. Change a number, re-run, get new parts.

```sh
FC=/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd
cd design && $FC case_v2.py
cd tools  && $FC verify_fit.py      # must say PASS
```

`case_v2.py` writes `design/case_v2_params.json` on every build. Every tool
reads its dimensions from there, so nothing can drift out of sync with the
model.

## Current design

| | |
|---|---|
| Outer | 102.60 x 46.55 x 11.35 |
| Wall / floor / lid | 1.60 / 1.20 / 1.60 |
| Board mounting | 4 printed pegs, 2.50 mm shoulder, press fit, no screws |
| Lid retention | Snap fit — 6 bead/groove pairs, 0.25 mm engagement |
| Lid location | 4 sleeves swallowing the pegs through the board |
| Openings | USB-C, battery cable, slide switch, microSD; lid: header block, 1x02 header, 2 buttons |
| Markings | `Cerelog` / `ESP-EEG V2` engraved 0.80 mm; `ON` `OFF` `microSD` at 0.50 mm |
| LED holes | 3 x 1.20 mm through the lid |

Fit is verified by boolean intersection against all 156 real board solids from
the KiCad STEP — not by eye. Latest result is in `design/verify_fit.txt`.

## Open items

See [`design/OPEN_ITEMS.md`](design/OPEN_ITEMS.md). The short version: **ON/OFF
may be reversed** (no electrical data exists in a STEP file), two LED holes
land inside the engraved title, and the power switch still needs a slider cap
to be usable.

## Not derivable from the files

Two 3D models in `v2_step.step` are wrong and are deliberately ignored:
`530480210` (battery connector height) and the unnamed `SOLID` / `SOLID001` /
`SOLID002`. Both confirmed by the board designer. If either turns out to be
real, case height and floor need revisiting.
