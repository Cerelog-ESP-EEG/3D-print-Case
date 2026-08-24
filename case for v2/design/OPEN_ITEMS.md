# Open items — v2 case

Ordered by how much damage each does if ignored.

## 1. ON / OFF may be reversed  — BLOCKING a production print

`ON` is engraved at X -38.00, `OFF` at X -27.00, flanking the slide-switch
actuator at X -32.46. Those positions come from the actuator's location and
its travel axis, both of which the STEP does give.

What the STEP does **not** give is anything electrical. There is no netlist, no
reference designator, no schematic. Nothing in any file available here says
which throw of `MK-12C02-G020` actually powers the board.

**Action:** meter a real board, or check the schematic. A case that labels the
power switch backwards is worse than one with no label at all.

## 2. Power switch is not usable — needs a slider cap

The actuator is a **1.30 x 1.16 mm nub** protruding 1.47 mm from the switch
body. It passes the board edge by only 1.00 mm.

```
actuator past board edge   1.00 mm
minus PCB-to-wall gap      0.30
minus wall (already thinned to 0.60)
= protrusion               0.10 mm
```

No wall thickness fixes this. Even at zero wall you would be sliding 0.70 mm of
a 1.3 mm-wide tab with a fingertip.

**Fix:** a third printed part — a socket that press-fits over the nub with a
paddle reaching out through the wall opening, widened to ~5 mm for a finger.
The existing 9.00 mm opening already has room for the travel. Not built yet.

## 3. Two LED holes pierce the engraved title  — cosmetic

| LED | Position | Lands in |
|---|---|---|
| `C2874118` | (-17.65, 2.53) | the `e` of `Cerelog` |
| `C2874116` | (-24.25, -4.07) | `ESP-EEG V2`, near `SP` |
| `C2874117` | (-39.60, -16.63) | clear |

The holes must stay over the LEDs, so the fix is to move the title. Shifting
the block to roughly Y +4.5 .. +20.5 clears both. Left alone because it is a
branding decision.

## 4. Header pin clearance rests on a modelled value

The 2.50 mm standoff leaves 1.09 mm below the modelled header pin tips
(-1.41 mm). That is the *model's* pin length. Two models on this board have
already turned out wrong, and clipped through-hole pins vary a lot with how
they are trimmed.

**Action:** caliper a real assembled board before committing to a batch.

## 5. Side-wall texture — not done, deliberately

A realistic moulded grain needs ~1800 shallow dimples. The boolean did not
complete in two minutes on a bare plate, and FDM cannot resolve a 0.18 mm
dimple anyway.

Use a **textured PEI build plate** instead. The lid prints top-face-down, so
the bed texture lands on the visible face and looks genuinely moulded.

Geometric texture on the side walls is additionally unsafe: they are locally
thinned to 0.60-0.80 mm at the switch, microSD and -X ports.

## 6. Lid STL has self-intersections in the engraved lettering

`case_v2_lid.stl` is **watertight, manifold, correctly oriented, correct
volume** — but carries 34 self-intersecting facet pairs.

All of them sit in the engraved letter walls, spanning 0.40 mm in Z (the
engraving depth). Isolated by testing each string on a bare plate:

| String | Self-intersects |
|---|---|
| `ON`, `OFF`, `Cerelog` | no |
| `microSD`, `ESP-EEG V2` | **yes** |

It is FreeCAD's ShapeString glyph tessellation, not the case geometry:

- Persists at every tessellation tolerance from 0.10 down to 0.01.
- Persists across Arial Bold, Arial, Arial Narrow Bold, Verdana Bold,
  Tahoma Bold and DIN Alternate — no font is clean for all three strings.
- Individual curved glyphs (`m c r o S D`) fail on their own at 3 mm; `i`
  does not. Larger sizes do not fix `microSD`.
- The underlying OCC solid is valid, with correct volume.

**Do not run FreeCAD's mesh repair on it.** The sequence
`fixSelfIntersections` / `removeFoldsOnSurface` drops the lid from
6501 mm3 to 2498 mm3 — it deletes real geometry and breaks solidity.

**Recommendation: print it.** Watertight + manifold + consistent normals are
what slicers actually need; self-intersections in engraved text are the most
common benign STL defect and are auto-repaired on import. If a slicer does
refuse, the one-line fallback is to empty `LABELS` and shorten the title.

`case_v2_base.stl` is completely clean on every check.
