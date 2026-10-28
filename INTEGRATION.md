# Play the integrated kart

Nine track-edge AI opponents now spawn in slots 1–9 in normal Play, with the player in slot 10. All karts share a 38 mph top speed and the current articulated kart model with distinct kart and driver colors. See Evidence/TenKartGrid/README.md for current validation. See `RACING_AI.md` for their implementation and validation. The user approved a later shared steering-limit adjustment from the original 65 to 240 coefficient for both the player and AI, retaining the movement formula, to negotiate the circuit's tight bends.

Open `Road_To_F1_New.uproject` in Unreal 5.8, open `/Game/RoadToF1/Maps/DesertKarting_Visual`, and press Play (Selected Viewport). Click the viewport for keyboard focus. W accelerates, S brakes/reverses, A/D steer, R resets to the assigned grid slot. Hold W through the five red lights; the existing ProofGameMode gate releases movement at lights-out. Stop and Play again to restart the countdown.

`Tools/PlayIntegrated.ps1` opens the same map as a standalone game preview. Use `-Editor` to open it in the editor instead. Normal play requires no diagnostic flags.

## Assets reused

The existing `AProofPawn`, `AProofGameMode`, RaceStartGantry and twenty GridStartSlot actors remain the gameplay implementation. There is one source module, one pawn class, and one authoritative countdown. Movement equations, collision sphere, input mappings and OnLightsOut implementation are unchanged.

`ULocalKartDriverVisuals` uses `/Game/RoadToF1/PlayerVisuals/FirstPerson/SK_FP_KartArms`, its existing skeleton and `A_FP_KartSteering`, plus `SM_FP_SteeringWheel`. Its additional `SM_PlayerKartChassis` is exported from `Art/DesertKarting/KartDriver_Fitted/Racing_Fit_v5/Kart_With_MakeHuman_Racer_v5.blend`. The 91 original non-wheel kart parts retain source dimensions, UVs and PBR textures. The fixed source rim/hub/spokes are excluded to avoid a duplicate wheel. The source Blender file is never saved or changed. Materials/textures live in the same FirstPerson folder under ChassisMaterials and are covered by the existing recursive PrimaryAssetLabel.

The seated camera is 95 cm above the source ground at X=0 cm with a restrained four-degree downward gaze. This keeps the source arm mesh's open shoulder ends outside the forward view while retaining the countdown overhead. All cockpit art is attached to the pawn and shares the full-size source coordinates, with wheel center (62,0,70) cm. Camera pitch never moves the kart or hands. FOV is 90 degrees, near clip is 3 cm, motion blur is disabled. No added camera shake. Head/helmet geometry is excluded. Both hands sample the same existing baked -25 to +25 degree steering animation as the wheel.

## Scope and limitations

The full-body V5 rig remains an editable Blender asset. The game uses its existing separate skinned arms/gloves, rather than importing an unbaked full-body rig. Glove/sleeve art remains a prototype. The original front wheels and chassis are present; their suspension, spinning and steering linkage are static, matching the source preview's limitations. Cosmetics add no collision: the original swept sphere remains the driving collision envelope. Kart extremities therefore do not acquire new physical collision. No production physics repository is modified.

## Reproduce evidence

Build Road_To_F1_NewEditor Win64 Development. Run Blender in background with `Tools/integrate_kart_export.py` to regenerate the chassis only. Run UnrealEditor with this project, `-ExecutePythonScript=<absolute path to Tools/integrate_kart_unreal.py> -KartIntegrationTest` to import, save/reload the visual map and request actual PIE. For subsequent validation without reimporting art, use `Tools/validate_integrated_pie.py` instead. The opt-in development-only test holds gameplay throttle, steers left/right on the grid, and captures 1600x900 driver-view screenshots and telemetry to `Evidence/Integration`. The script checks the final telemetry timestamp to exclude stale evidence. Normal play never overrides player input.

The validation script asserts a single gantry, twenty start slots, no placed duplicate pawn, and preserved map actor transforms/mesh/material references across save/reload. Native telemetry records PIE world type, gate state, red count, movement and single start event. See the evidence directory for actual results; successful compilation alone does not establish runtime success.

