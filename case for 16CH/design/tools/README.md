# tools/

Verification and preview scripts for the 16CH case. None of these change the
design — `../case_16ch.py` is the only file that does.

They all read dimensions from `../case_16ch_params.json`, which `case_16ch.py`
rewrites on every build. Nothing hard-codes a Z value.

## The loop

```sh
FC=/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd

cd ../ && $FC case_16ch.py         # 1. build   -> stl/, Case files FreeCAD/, params
cd tools/
$FC verify_fit.py                 # 2. check   -> ../verify_fit.txt   MUST say PASS
$FC export_board_mesh.py          # 3. meshes for the renderer
python3 render_preview.py         # 4. picture -> ../preview.png
$FC build_assembly.py             # 5. case + board document
/Applications/FreeCAD.app/Contents/MacOS/FreeCAD show_assembly.py   # 6. open it
```

`measure_board.py` is run-once tooling: it produced
`../16ch_raw_measurements.txt`, which `../16ch_measurements.md` is written
from. Re-run it if the board is re-exported.

## What each does

| Script | Runs under | Purpose |
|---|---|---|
| `measure_board.py` | freecadcmd | Extracts board outline, mount holes, every solid's extents, below-board protrusions and edge-proximate parts. |
| `verify_fit.py` | freecadcmd | Every board solid vs base and lid, plus base-vs-lid, peg/sleeve mate, LED holes, DIP switch floor access and port alignment. Writes `../verify_fit.txt`. |
| `export_board_mesh.py` | freecadcmd | Tessellates the board for the renderer. Coarse; pictures only. |
| `render_preview.py` | python3 | Six-view z-buffer render to `../preview.png`. |
| `build_assembly.py` | freecadcmd | Rebuilds `assembly_16ch.FCStd` (case + board). |
| `show_assembly.py` | FreeCAD GUI | Opens it with everything visible, lid translucent. |
| `_paths.py` | — | Shared paths, params loader, bad-model list. |

## Four mistakes baked in as guardrails

**`verify_fit.py` uses a 0.001 mm3 threshold.** On the V2 case it was 0.5, and
that hid a real 0.09 mm3 collision — the check reported a clean fit that was
not clean. Do not raise it.

**`render_preview.py` uses a z-buffer, not depth sorting.** The painter's
algorithm version drew engraved text through the solid lid, which read as the
engraving cutting clean through when it was 0.80 mm into 1.60 mm. Do not
"simplify" it back to sorting triangles.

**`verify_fit.py` also checks port *alignment*, not just interference.** A
no-collision result only proves nothing touches; it does not prove an opening
is actually in front of a connector. The port check sweeps each connector's own
footprint outward through its wall and looks for material in the way.

**`verify_fit.py` measures whether the engraving perforates the lid.** On V2 a
bad preview render made the 0.80 mm engraving look like a through-cut and there
was no measurement to settle it. The check now boxes the lid from the plate
underside up to each engraving floor and reports the void volume — it must be
0.0000 mm3.

## Known-bad models in 16ch_step.step

Confirmed wrong by the board designer on the V2 export; the same models appear
here. Skipped by every check:

- `530480210` — battery connector, height wrong.
- `SOLID`, `SOLID001`, `SOLID002` — unnamed, claim 4.21 mm below the board.

They live in `_paths.BAD_MODELS_*`. If either turns out to be real, the case
height and floor both need revisiting.

`_paths.TOP_LEVEL` additionally drops the STEP's top-level compound
`"16chpcbcad 1"`, which repeats every child shape. Note the sub-parts
`"16chpcbcad 1.211"` ... `"1.216"` are **real** bottom-side solids and are kept.
