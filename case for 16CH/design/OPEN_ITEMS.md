# Open items — 16CH case

Ordered by how much damage each does if ignored.

## 1. DIP switches are recessed 1.82 mm, not proud  — needs a decision

The two `DHA-08TQR` 8-position DIP switches are on the underside of the board
and each has a through-opening in the case floor (12.90 x 9.70 mm, 0.80 mm
clearance all round). They are reachable with a pen tip. They do **not** sit
flush with the outside of the case.

Measured: switch underside sits at case Z **1.82**; the outside of the floor
is Z 0.00.

This is a hard geometric conflict, not an oversight:

```
switch underside   = FLOOR_T + BOSS_H - 2.385
flush with outside => FLOOR_T + BOSS_H = 2.385
with FLOOR_T 1.20  => BOSS_H = 1.185
but the header pins protrude 1.405  => they would hit the floor
```

Making the switches flush requires dropping `BOSS_H` from 3.00 to about 1.60
**and** adding relief pockets under every header pin row. That is the opposite
of "more clearance under the board", so it was not done.

**If you want them proud instead of recessed, say so** — it is `BOSS_H` plus a
`FLOOR_RELIEF` list, both already wired into `case_16ch.py`.

## 2. ON / OFF may be reversed — carried over from V2, still unresolved

`ON` is engraved at X -49.00, `OFF` at X -34.50, flanking the slide-switch
actuator at X -41.96. Those positions come from the actuator's location and
travel axis, which the STEP does give.

What the STEP does **not** give is anything electrical — no netlist, no
reference designators, no schematic. Nothing available here says which throw
of `MK-12C02-G020` actually powers the board.

**Action:** meter a real board, or check the schematic. Same open item as V2;
if it was resolved there, the answer carries over unchanged (same part, same
orientation).

## 3. Power switch still needs a slider cap

The actuator is a 1.30 x 1.16 mm nub. On this board it passes the board edge
by 0.36 mm:

```
actuator past board edge   0.36 mm
minus PCB-to-wall gap      0.30
minus wall (thinned to 0.60)
= it does not reach the outside face at all
```

Worse than V2, which had 1.00 mm of overhang. The 10.10 mm wall opening has
room for the travel, but you cannot work the switch with a fingertip. It needs
a third printed part: a socket that press-fits over the nub with a paddle
reaching out through the opening. **Not built.**

## 4. The -Y lid rim is interrupted over 52 mm

The 2x20 electrode header body stops **0.06 mm** short of the lid rim's inner
face, so the opening for it has to take the rim with it. Over X 0.30..52.30
the lid has no rim — just a 1.735 mm ledge of plate sitting on the 1.60 mm
base wall.

The opening is Y -23.60..-12.40, i.e. **11.20 mm** across a 5.08 mm header
body. It was widened 4.00 mm inboard on purpose, for finger room when seating
ribbon cables; the outer edge stayed at the wall.

Consequences, all accepted deliberately:

- No snap segments are possible on the -Y wall over that span. Retention there
  comes from the +Y wall (4 segments) and the two ends (3 segments). V2 used
  +/-Y only; this case uses all four walls.
- The lid is less stiff along that edge than V2's. If it bows in practice, the
  fix is a rib on the underside inboard of the opening, not a thicker lid.

## 5. Header pin clearance rests on a modelled value

`BOSS_H` 3.00 leaves 1.60 mm below the modelled header pin tips (-1.405) and
0.62 mm below the DIP switches (-2.385). Those are the *models'* values. Two
models in the V2 export already turned out wrong, and clipped through-hole
pins vary a lot with how they are trimmed.

**Action:** caliper a real assembled board before committing to a batch. The
DIP switch height in particular is worth checking — it is now the part that
sets the standoff.

## 6. Both STLs have self-intersecting facet pairs — benign, print them

`case_16ch_lid.stl` is **watertight, manifold, correctly oriented, and its
mesh volume matches the solid exactly** (9140.0 vs 9140.0 mm3) — but carries
24 self-intersecting facet pairs.

All of them sit between Z 10.90 and 11.65, i.e. inside the engraved lettering:
the `ON`/`OFF`/`microSD` label row and the title block. This is FreeCAD's
ShapeString glyph tessellation, not the case geometry — the same defect V2 had,
in the same strings. The count rose from 16 when the title was shrunk from
7.0 mm to 4.5 mm; smaller glyphs tessellate into more slivers. It is the same
benign class of defect either way.

No engraving perforates either part — `verify_fit.py` measures the void under
every engraved string and reports 0.0000 mm3 for all seven. Thinnest remaining
material is 0.80 mm under the lid title (of 1.60 mm) and 0.70 mm under the
bottom mode legend (of 1.20 mm).

**Do not run FreeCAD's mesh repair on it.** On V2 the sequence
`fixSelfIntersections` / `removeFoldsOnSurface` deleted real geometry and
broke solidity.

**Recommendation: print it.** Watertight + manifold + consistent normals is
what slicers actually need. If a slicer refuses, the one-line fallback is to
empty `LABELS` in `case_16ch.py` and rebuild.

`case_16ch_base.stl` carries **42** pairs, all in Z 0.00..0.50 — the band of
the bottom-face mode legend, i.e. the same glyph-tessellation defect. It was
completely clean before that legend was added. Both parts are watertight,
manifold, correctly oriented, and match their solid volumes
(base 11277.4 vs 11277.6, lid 9140.0 vs 9139.9 mm3).

## 7. Side-wall texture — not done, deliberately

Same reasoning as V2: use a **textured PEI build plate**. The lid prints
top-face-down so the bed texture lands on the visible face. Geometric texture
is additionally unsafe on the side walls here — they are locally thinned to
0.60-0.80 mm at the switch, microSD and -X ports.
