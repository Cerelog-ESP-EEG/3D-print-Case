# tools/

Verification and preview scripts for the v2 case. None of these change the
design — `../case_v2.py` is the only file that does.

They all read dimensions from `../case_v2_params.json`, which `case_v2.py`
rewrites on every build. Nothing hard-codes a Z value.

## The loop

```sh
FC=/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd

cd ../ && $FC case_v2.py          # 1. build   -> stl/, Case files FreeCAD/, params
cd tools/
$FC verify_fit.py                 # 2. check   -> ../verify_fit.txt   MUST say PASS
$FC export_board_mesh.py          # 3. meshes for the renderer
python3 render_preview.py         # 4. picture -> ../preview.png
$FC build_assembly.py             # 5. case + board document
/Applications/FreeCAD.app/Contents/MacOS/FreeCAD show_assembly.py   # 6. open it
```

## What each does

| Script | Runs under | Purpose |
|---|---|---|
| `verify_fit.py` | freecadcmd | Every board solid vs base and lid, plus base-vs-lid, peg/sleeve mate, LED holes. Writes `../verify_fit.txt`. |
| `export_board_mesh.py` | freecadcmd | Tessellates the board for the renderer. Coarse; pictures only. |
| `render_preview.py` | python3 | Six-view z-buffer render to `../preview.png`. |
| `build_assembly.py` | freecadcmd | Rebuilds `assembly_v2.FCStd` (case + board). |
| `show_assembly.py` | FreeCAD GUI | Opens it with everything visible, lid translucent. |
| `_paths.py` | — | Shared paths, params loader, bad-model list. |

## Two mistakes baked in as guardrails

**`verify_fit.py` uses a 0.001 mm3 threshold.** It was 0.5, and that hid a real
0.09 mm3 collision — the check reported a clean fit that was not clean. Do not
raise it.

**`render_preview.py` uses a z-buffer, not depth sorting.** The painter's
algorithm version drew engraved text through the solid lid, which read as the
engraving cutting clean through when it was 0.80 mm into 1.60 mm. Do not
"simplify" it back to sorting triangles.

## Known-bad models in v2_step.step

Confirmed wrong by the board designer, skipped by every check:

- `530480210` — battery connector, height wrong.
- `SOLID`, `SOLID001`, `SOLID002` — unnamed, claim 4.21 mm below the board.

They live in `_paths.BAD_MODELS_*`. If either turns out to be real, the case
height and floor both need revisiting.
