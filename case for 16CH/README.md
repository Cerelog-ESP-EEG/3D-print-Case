# Cerelog ESP-EEG 16CH — 3D printed case

Snap-fit two-part enclosure, **120.30 x 50.67 x 11.65 mm**. No screws.

**Printing? Go straight to [`stl/PRINT.md`](stl/PRINT.md).**

## Folders

| Folder | What lives there |
|---|---|
| **`stl/`** | The two printable STLs and `PRINT.md`. This is all you need at the printer. |
| **`Case files FreeCAD/`** | FreeCAD documents — the case on its own, the case with the board in it, and the original KiCad STEP export. |
| **`design/`** | The parametric source, measurements, build log, previews, and `tools/`. |

## Seeing the whole assembly in FreeCAD

```sh
/Applications/FreeCAD.app/Contents/MacOS/FreeCAD "design/tools/show_assembly.py"
```

That opens `Case files FreeCAD/assembly_16ch.FCStd` — base, lid and all 220
real board solids in their true positions — with everything made visible, the
lid at 60% transparency and the base at 25% so you can see the fit. A document
built headlessly has no saved GUI state, so opening the file directly will show
most objects hidden; run it through that script the first time.

## How the design is built

The case is **not modelled by hand**. `design/case_16ch.py` builds both parts
from named constants and exports the STLs. Change a number, re-run, get new
parts.

```sh
FC=/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd
cd design && $FC case_16ch.py
cd tools  && $FC verify_fit.py      # must say PASS
```

`case_16ch.py` writes `design/case_16ch_params.json` on every build. Every tool
reads its dimensions from there, so nothing can drift out of sync with the
model.

## Current design

| | |
|---|---|
| Outer | 120.30 x 50.67 x 11.65 |
| Wall / floor / lid | 1.60 / 1.20 / 1.60 |
| Board mounting | 4 printed pegs, 3.00 mm shoulder, press fit, no screws |
| Lid retention | Snap fit — 9 bead/groove pairs on all four walls, 0.25 mm engagement |
| Lid location | 4 sleeves swallowing the pegs through the board |
| Base openings | USB-C, battery cable, slide switch, microSD, **2 DIP switch holes in the floor** |
| Lid openings | 2x20 electrode header, 1x02 header, 2x 1x01 pins, 2 buttons |
| Markings, lid | `Cerelog` / `ESP-EEG 16CH` engraved 0.80 mm; `ON` `OFF` `microSD` at 0.50 mm |
| Markings, base | DIP switch mode legend: `Diff Mode` (-X side) and `SRB1 Mode` (+X side), 3.40 mm text, rotated 90 deg so the arrows run along the DHA-08TQR travel axis. `Diff` points toward the connector edge, `SRB1` away. 0.50 mm deep, mirrored to read when the case is rolled over |
| LED holes | 3 x 1.20 mm through the lid |

Fit is verified by boolean intersection against all 220 real board solids from
the KiCad STEP — not by eye. Latest result is in `design/verify_fit.txt`.

## What changed from the V2 case

Three things drove the redesign; everything else is carried over.

1. **The electrode header moved to the -Y edge** and grew from 2x12 to 2x20.
   Its body stops 0.06 mm short of the lid rim's inner face, so the lid opening
   has to cut the rim away over 52 mm. Snap segments moved onto all four walls
   to compensate — V2 used the two long walls only.
2. **Two `DHA-08TQR` 8-position DIP switches are now on the underside** of the
   board, hanging 2.385 mm below it. They set the standoff height (`BOSS_H`
   3.00, up from V2's 2.50) and each gets a through-opening in the floor.
3. **The board grew** 98.80 x 42.75 -> 116.50 x 46.87.

Full comparison in [`design/16ch_measurements.md`](design/16ch_measurements.md).

## Open items

See [`design/OPEN_ITEMS.md`](design/OPEN_ITEMS.md). The short version: the DIP
switches are recessed 1.82 mm rather than proud (a hard conflict with header
pin clearance — read item 1 before printing a batch), **ON/OFF may be
reversed**, and the power switch actuator no longer reaches the outside face at
all, so it needs a slider cap.

## Not derivable from the files

Two 3D models in `16ch_step.step` are wrong and are deliberately ignored:
`530480210` (battery connector height) and the unnamed `SOLID` / `SOLID001` /
`SOLID002`. Both confirmed by the board designer on the V2 export; the same
models are present here. If either turns out to be real, case height and floor
need revisiting.
