# Circuit development

Open `Road_To_F1_New.uproject` in Unreal 5.8.3, then `/Game/RoadToF1/Maps/CircuitDevelopment`. Press Play and click the viewport: W/S accelerate/brake/reverse, A/D steer, R resets. Alternatively run `Tools/OpenCircuit.ps1 -Profile Balanced`. VisualProof remains the default and is unchanged. No C++ gameplay, input, race or AI files were changed.

Phase 1 uses the earlier project's recorded 600-point Race_20KartField route, resampled to 2400 points. It is **not surveyed South Garda**. The relative layout is preserved, translated to the existing pawn spawn. Width is an authored 8 m; road height variation is deliberately mild. `Art/CircuitDevelopment/layout.json` records provenance and `geometry.json` records translation, dimensions and generated assets. Blender source contains the editable centerline. Road/shoulders are divided into modules; terrain is tiled.

The ordered Blender scripts are `circuit_geometry.py`, `circuit_textures.py`, `circuit_environment.py`. Unreal authoring scripts are `circuit_phase1.py`, `circuit_phase2.py`, `circuit_phase3.py`. Each later phase requires the preceding saved validation gate. Accepted passes are protected from accidental reruns. Use a versioned working copy for regeneration. Original per-phase map backups are in `Evidence/CircuitDevelopment/Backups`.

Assets live under `/Game/RoadToF1/CircuitDevelopment/{Meshes,Materials,Textures,Props,Instancing}`. Asphalt reuses the existing CC0 Poly Haven Asphalt Track maps at 2 m. Concrete, gravel, soil, ground sward, wear masks and secondary props are original procedural artwork, **not scans**. Clouds use the built-in Unreal material. No marketplace content was downloaded/imported.

Tire walls use simple blocking boxes beyond the racing corridor. Wire fences, signs and grates are noncolliding. Repeated props use instancing and 140–240 m culling. The overhead validation capture temporarily extends culling to show full placement; runtime settings remain bounded.

Remaining visual gaps: licensed 3D grass clumps/bushes, European trees with LODs, reference-backed paddock structures, scanned ground/curb replacements and a detailed rigged cockpit. Ground remains visibly flat close to the camera; the scene does not meet the supplied photographic benchmark. Scenery production is partial until those assets are supplied.

Evidence and phase checks: `Evidence/CircuitDevelopment`. Driver and Overview camera positions are consistent across phases; Ground was adjusted after Phase 1 for a useful close curb inspection. No commits or pushes were made.
