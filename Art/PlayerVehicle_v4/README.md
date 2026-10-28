# Player vehicle V4

Editable source: `PlayerVehicle_v4.blend`; rebuild with `D:/Boring/blender.exe -b --python build.py`. `Exports/` contains individually pivoted FBX meshes and the two weighted driver variants. `manifest.json` records dimensions, origins, source hash, materials, and baked wrist-target error. Source art is reused from Cockpit_Layout_v5 and Art/RacingAI; the original Blender files, FBXs and any accompanying provenance remain in their original locations.

Unreal content: `/Game/RoadToF1/PlayerVehicleV4`. The native `UKartMechanicalVisuals` component is attached to the existing `AProofPawn`. Open `Road_To_F1_New.uproject`, load `/Game/RoadToF1/Maps/DesertKarting_Visual`, and Play. Existing input bindings and the camera toggle remain in use. `Tools/PlayIntegrated.ps1` opens the playable project.

## Mechanism

All runtime geometry is collision-free and rooted at pawn Z -31 cm. X is forward, Y right, Z up. Blender metre coordinates are exported to Unreal centimetres with the FBX Y-axis conversion. Front axle X = 60 cm; rear axle X = -44 cm; tire-centre track = 106 cm. Measured front/rear radii are 17.589/20.938 cm. These preserve the inherited wheel geometry; the inherited overall bodywork is larger than the supplied concept.

The steering shaft is inclined 55 degrees. The pitman pin and two steering-arm pickups form fixed-length rods. A continuous linkage solve finds the column angle whose mean left/right road-wheel angle matches the authoritative tire steering angle. The inner wheel turns farther; this is partial Ackermann from a linkage, rather than mathematically ideal Ackermann. No physics coefficients are changed. The bake covers +/-45 degrees of column rotation; normal 24-degree tire lock uses less than that range. The fixed-grip arm poses use two-bone IK with the existing weighted fingers. Both driver renderers sample the same action; leg IK follows the pedals.

Wheel roll is independent of kingpin yaw. Front roll projects local velocity and yaw velocity onto each wheel's forward direction. Rear wheels, axle, sprocket and brake disc share one rotation. The current tire state has no angular-speed state: axle spin is a signed ground-speed approximation, including during slip. It does not simulate wheelspin or brake lockup. A fixed instanced chain follows the sprocket path, with a matching output-sprocket rotation.

Rendering runs in PostUpdateWork, after pawn simulation and race-staging timers. It reads state and inputs; it does not advance simulation or apply forces. No suspension or scripted drift yaw is added. The existing restrained camera effects remain available. The camera position derives from the seated head pose plus an eye offset.

## Validation and limits

Actual engine output is in `Evidence/PlayerVehicle_v4`. `automation.log` records the 481-angle fixed-rod sweep. `validation.json` and `motion.csv`, when produced by `Tools/validate_player_vehicle_v4.py`, are the actual PIE result and frame samples. A failure is not a pass; inspect the JSON booleans and any `pie_error.txt`. Blender previews are not Unreal evidence.

The available racer is a reused weighted mesh, not a newly tailored production suit. Shoulder/cuff seams, glove surface fit, seat contacts and bodywork proportions need artistic finishing. High-density inherited meshes have no dedicated performance LOD set. No whole-body intersection-free or photorealistic claim is made. Pedal brake input is binary because the existing controls expose a brake button. No hand-over-hand animation is introduced. No new third-party assets were downloaded.

## Rollback

Launch with `-LegacyKartVisuals` for the prior playable cockpit/exterior assets. The new component then does not initialize. For source rollback, restore only `ProofPawn.cpp/.h` and `LocalKartDriverVisuals.cpp/.h` from this folder's `Backup/`, remove the new KartMechanicalVisuals/KartVisualKinematics source and test, and rebuild. The backups preserve the pre-task working copies (the previously unchanged LocalKartDriverVisuals.h comes from HEAD). Do not reset unrelated working-tree changes. Existing source art and Unreal assets were not replaced. No commit or push is part of this work.
## Rebuild order

Run Blender `build.py`, then `finalize_scene.py` once on that newly built file. `finish_materials.py` can update the saved assembly and static exports independently. Run Unreal's Python commandlet with `Tools/import_player_vehicle_v4.py`; this saves the shared skeleton and applies the versioned metal materials. Build the Editor target before Play. The repair scripts document the existing source integration work; they are not required for ordinary Play.

The final PIE test permits at most 0.1 seconds after the race-reset call before comparing steering diagnostics, because reset occurs after that frame's component update. All driving samples retain the normal 0.05-degree steering-agreement bound. The test pad, capture camera and collision wall are transient; no map is saved.

## Final result

The final native build succeeded (`build_final_link.log`). The final actual PIE run passed all A–L functional checks over 1,178 samples: maximum rod-length error 0.000000317 cm; maximum wrist position error relative to the steering wheel 0.00548 cm. These measure transforms, not glove/rim surface contact. Seven numbered screenshots and `Evidence/PlayerVehicle_v4/steering_sequence.html` contain actual Unreal captures. `RESULTS.md` explains the evidence and remaining art limitations. The earlier `pie_error.txt` records a superseded failed attempt; the final result is `validation.json`.

The source shaft/steering-arm geometry and 45-degree rig bake determine column travel. There is no artist-facing independent lock-to-lock slider; changing that geometry requires regenerating and validating the arm bake. Dedicated cloth, hand-over-hand, torso inertial animation and contact-driven chassis flex are not supplied. The inherited weighted gloves retain imperfect finger wrap and require sculpt/skin finishing for close-up production use.
## Gloved grip update

The subsequent hand revision is documented in `Hands/README.md`. It replaces the stretched inherited glove surfaces with continuous skinned palms, individual curled fingers and opposed thumbs, and refits both wrists to the wheel. Reproduce this revision with `Hands/fit_grip.py` after the base assembly build; use `Tools/import_player_vehicle_v4_grip.py` to import only the two driver meshes and their animation. The previous grip and Unreal packages are backed up under `Hands`.
