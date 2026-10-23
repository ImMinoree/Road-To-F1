# DesertKarting route review

The existing `/Game/RoadToF1/Maps/DesertKarting` and `DesertKarting_Visual` maps receive the same additive readability layer. There is no new demonstration circuit. Open either existing map normally; the Visual map retains its spectator-preview default, and the original map retains its first-person driving mode. No C++ compilation, input, camera, lighting, exposure, sky, race rules, or pit junction changes are made.

## Source route and annotated evidence

`audit.json` reproduces the main `track=path(...)` centreline from the supplied source generator and compares the main racing mesh against the native `desert_karting.blend`. All 1,496 vertices match the GLB exactly; native 748 quads correspond to 1,496 GLB triangles. The resulting main route is 1,040.02 m long, one connected surface, with two boundary loops, no non-manifold edges, and no detected nonlocal asphalt overlaps above 0.03 m² (excluding neighbouring sections within 25 m along the route). The inside-width curvature clamp reduces some turns from nominal 12.6 m to a minimum of approximately 8.22 m.

The user confirmed +X travel on the main straight, matching the source path and original kart-heading generator. C1–C7 identify analytically grouped turn complexes in that order; they are **not official circuit corner numbers** or a surveyed racing line.

`Evidence/DesertRoute/Before_*_TopDown.png` and `After_*_TopDown.png` are real Unreal screenshots, captured straight down with a **-90° orthographic camera**, not a perspective aerial or a generated drawing. Identical camera: location (2500,-7000,40000) cm, yaw/roll zero, ortho width 33500 cm, 2400×2000, aspect 1.2. Image right is +Y; image up is +X. `*_Annotated.png` files are deterministic overlays on those unchanged captured backgrounds: source path, travel arrows, numbered turn complexes, gantry/finish and proposed pit endpoints. The outer access road is separate from the main racing route. Source unannotated images are retained alongside annotations.

## Verified defects and reversible fixes

* Original checkerboard geometry lies at Z=0.135 m, below the road at Z=0.16 m, and only spans part of the carriageway. Add a full-width 12 m checkerboard at the **existing gantry station**, X=-18 m, raised 1.8 mm above the road. No original vertices or materials are edited.
* Hidden kart/driver groups still had active collision. Before probes hit hidden kart geometry at 31 road samples / 16 swept segments in DesertKarting, and 57 samples / 28 segments in its Visual variant. Disable actor collision and component collision on these eight hidden groups in each map. Their meshes, Blueprints, materials and files remain intact.
* Add 22 sparse source-aligned direction arrows, using one instanced mesh type, and seven numbered boards in one batched mesh. Board positions are checked against the source asphalt to keep their centres at least 1 m off every racing-road section, not just their local bend. All new overlays/signs have NoCollision profiles and actor collision disabled. No safety barrier was found blocking the sampled racing corridor, so no barriers were relocated.

The only new mesh assets are `SM_Route_Arrow`, `SM_Route_Finish`, and `SM_Route_CornerBoards`, under `/Game/RoadToF1/DesertRoute`; they reuse existing materials. `RouteReadability.blend` and FBXs retain their reproducible source. Existing mesh assets, native Blender scene, GLB, material assets, source code, and unrelated maps are protected by hashes.

## Pit lane: proposals, not verified junctions

The user specified proposed A-entry at X=-38.5 m and proposed B-exit at X=44.5 m, in the +X direction. Both endpoints are at pit centre Y=-17 m. **No pit connectors, tapers, barrier openings, junction markings, or geometry changes were created.** These labels appear only in the annotated review map.

At A, the rectangular pit pavement overlaps approximately 4.03 m of the main asphalt cross-section near the returning bend. This geometric contact is not a deliberately designed or approved entry taper. At B, the pit edge stops approximately **5.74 m short of the main asphalt**, across the verge/runoff area. The pit lane therefore cannot yet be treated as a verified entry-to-exit racing facility. `pit_geometry_sections` in `audit.json` contains the exact transverse asphalt intervals; live Unreal lateral probes are also recorded.

Runoff and infield have collision, and the temporary ProofPawn has no checkpoint or off-track enforcement. **Off-track shortcuts remain physically possible.** Mesh connectivity alone does not prove their absence. Additional approved safety layout or future race-rule integration is needed; neither is invented during this review.

## Validation and undo

`Before_validation.json`, `After_validation.json` and final `Final_validation.json` record live-editor tests for both maps: three support rays at each of 748 source samples (centre and ±1.8 m), plus a 28 cm radius swept sphere along all 748 centreline segments, matching the temporary pawn radius. The final pass follows the explicit nonblocking-paint profile correction. Raw intermediate results are retained rather than replaced with success claims. Tests are geometric/physics-query checks, not a completed timed driving lap or a future full-size kart dynamics test.

Checkpoints `/Game/RoadToF1/Checkpoints/DesertKarting_BeforeRoute` and `DesertKarting_Visual_BeforeRoute` retain each pre-change map. `restore_state.json` records the original hidden-kart collision modes; these checkpoints deliberately preserve the old invisible-collider defect for comparison. To remove only the new signs/paint safely, run `Tools/desert_route_undo.py` in Unreal's Execute Python Script command; it keeps parked karts hidden and non-colliding. No source assets are deleted. Exact checkpoint restoration should only be used intentionally, since it restores the hidden collision problem too.
