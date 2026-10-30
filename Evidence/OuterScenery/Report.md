# DesertKarting_Visual â€” outside scenery

Target: /Game/RoadToF1/Maps/DesertKarting_Visual

Added two layered dune terrain meshes spanning approximately 280â€“1,380 metres from the venue centre, plus a separate irregular mountain range extending to approximately 2.9 km. The six previous low ridges remain as intermediate foothills. Added 107 sparse desert scrub instances and 38 instances of the existing SM_ED_Rock, grouped outside the 240 m venue envelope. All scattered items were grounded by terrain traces; no placements were rejected.

New assets: /Game/RoadToF1/OuterScenery/{Meshes,Materials,Instancing}. Editable source: Art/OuterScenery/OuterScenery.blend. Existing rock reused from /Game/RoadToF1/EnvironmentDepth/Meshes/SM_ED_Rock. Existing sand materials reused or copied into scenery-only instances. The far mountain material provides restrained atmospheric fill; no sky, light, fog, exposure or camera settings were changed.

The landscape has 110,592 triangles at full detail across three meshes, each with 45% and 15% reduction LODs. Two 720-triangle scrub variants also have three LODs. Six HISM groups hold 148 new instances total. Scattered props cull at 550 m; terrain remains visible to the horizon. All additions disable collision and shadow casting. No particles, transparency layers or new light actors.

The map was saved and reloaded. Existing actor/lighting/camera signatures and tire instance transforms matched. 2,264 kart-sized clearance sweeps matched the baseline exactly: eight pre-existing outer-edge hits remained, with zero new obstructions. This was a scenery clearance check, not a new driving-physics test.

Matching before/after first-person PIE views cover the start/finish straight, hairpin and western corner. Screenshots use the existing player camera and its unchanged FOV. The pawn was repositioned only in the temporary inspection session. PIE shots are the actual rendered engine output; comparison sheets merely place images side by side.

Performance probes were capped near 60 fps and are insufficient to establish a precise GPU-cost change. LODs, instancing and collision/shadow disabling are verified; no claim of zero rendering cost. Earlier offscreen editor sessions exited with an access violation during shutdown after successful captures/saving; this does not establish a clean shutdown lifecycle.

This pass edits no source, gameplay, AI, physics, inputs, track materials, kerbs, pits or cockpit assets. Source/config hash audit detected a concurrent RaceStartGantry.cpp edit during another build; that separate edit was preserved. No commit or push.

Checkpoint: Evidence/OuterScenery/Checkpoint/DesertKarting_Visual.umap. Restore only when Unreal is closed, and account for any subsequent map edits before using it. New assets are isolated under OuterScenery.

Play: open Road_To_F1_New.uproject, load DesertKarting_Visual and press Play.

Final validation completed successfully (editor exit code 0). Six before/after PNGs passed signature, chunk CRC and pixel-stream decompression checks. Final images use verified_*00000.png; intermediate after_* and final_* files are superseded. Open BeforeAfter.html for all three matched comparisons.

Final capped frame-time medians: before_straight 16.66 ms, before_hairpin 16.65 ms, before_west 16.67 ms, verified_straight 16.67 ms, verified_hairpin 16.68 ms, verified_west 16.66 ms. These capped samples are not a GPU benchmark.
