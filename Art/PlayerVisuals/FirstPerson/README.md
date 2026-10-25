# Local-player cockpit visuals

Update: the integrated DesertKarting_Visual game now includes the original V5 chassis, seat and front wheels at full scale, sharing the animated arms/wheel source coordinates. See `INTEGRATION.md` at the project root for current Play instructions, camera alignment, evidence and limitations. The camera transform and chassis integration described there supersede the earlier arms-only alignment below.

Separate first-person **placeholder** adapted from the existing MakeHuman V5 gloves and sleeves. It adds shaped suede reinforcement, geometric sewn edging and microfiber normal textures. It is editable, skinned 3D geometry, not a rendered image. It is not a finished photorealistic glove asset: finger construction, cuff transitions, cloth folds and seam finish need manual art work.

## Files

- `FP_KartArms.blend`: independent 53-bone grip-bind rig, arms/gloves, baked steering and preview wheel.
- `Exports/SK_FP_KartArms.fbx`: skeletal mesh and 2-second steering pose clip; do not retarget onto the full-body skeleton.
- `Exports/SM_FP_SteeringWheel.fbx`: isolated visual wheel with centered rotation pivot.
- `fp_center.png`, `fp_left.png`, `fp_right.png`: genuine Blender Cycles previews.
- Unreal: `/Game/RoadToF1/PlayerVisuals/FirstPerson`. Main assets: `SK_FP_KartArms`, `A_FP_KartSteering`, `SM_FP_SteeringWheel`.
- Validation logs, import manifest and runtime captures: `Evidence/FirstPerson` under the project directory.

## Player-only integration

`AProofPawn` creates `ULocalKartDriverVisuals`. Its existing steering axis is passed to `SetSteeringInput`; the component never supplies movement, collision, forces, input or replicated gameplay state. The visual components have collision, overlap, physics, navigation influence, shadows and ray-tracing visibility disabled.

The component creates its transient camera-attached arms and wheel only when the pawn is locally controlled by a local `APlayerController` with a `ULocalPlayer`, is the view target and has an active cockpit camera. AI, remote controllers and dedicated servers do not create them. Both meshes use `OnlyOwnerSee`, so another split-screen view does not see the first player's arms. All cosmetic components are nonreplicated. Each multiplayer client independently creates the visuals for its own pawn; no cosmetic RPC is required.

The runtime prototype currently has **no full-body skeletal driver component on its pawn**. Existing full-body Blender assets and static world/AI kart visuals are preserved. When a third-person driver renderer is attached to the same pawn, call `SetThirdPersonDriver(Mesh)` or give that mesh the `ThirdPersonDriver` component tag before BeginPlay. The component then applies `OwnerNoSee` only while the local cockpit is active, restoring the renderer's previous setting when disabled/unpossessed. It never globally hides the body or changes remote/AI meshes. World static combined kart/driver meshes are deliberately not guessed or hidden.

## Steering and fit

The independent clip samples the source V5 steering poses from -25° through center to +25°. Normalized input [-1,1] selects the same sample time for the arms and rotation for the visual wheel. Animation runs after the cosmetic tick to avoid a one-frame wheel/hand mismatch. Maximum supported wheel rotation is ±25°; extending that range requires new poses.

Source wheel center is (62,0,70) cm and radius 18.4 cm. The imported scene uses centimeters, +X forward, +Z up, with Blender Y mirrored. The complete visual pair shares a camera-relative art transform: 0.85 uniform scale, source eye (0,0,95) cm and 12° visual pitch. This fits the current prototype camera without changing its transform or kart physics. `CockpitVisualTransform` is editable for a later physical kart cockpit; avoid showing a second owner-visible steering wheel in that cockpit.

`SetCockpitEnabled(false)` restores the third-person owner view. Missing/incompatible first-person assets fail safely without hiding the body. `PAL_LocalCockpit` labels the new folder for cooking; a packaged-build cook is still required to verify distribution.

## Validation and rerun

Completed on Unreal Engine 5.8.3: Editor build, asset import, `OwnershipAndSteering` automation test (passed), actual standalone center/left/right captures, and 49 Blender poses checked against the rim. The closest checked glove vertex stayed about 0.79 mm outside the measured rim; no tested vertex penetrated it. This vertex-to-torus check does not prove watertight triangle collision. Imported hand bones match source samples within 5 mm. Runtime images were visually reviewed after correcting skeletal material usage flags.

The already-open editor was left running and does not automatically load the new native module. Restart it before testing Play, or use `Tools/PreviewFirstPerson.ps1` to open a separate game preview. No map needs to be saved.

Build `Road_To_F1_NewEditor`, then run the automation test `RoadToF1.PlayerVisuals.OwnershipAndSteering`. It covers two local ownership chains, remote/AI exclusion, visibility restoration, no collision/replication, five imported hand-bone steering samples against Blender, and unchanged pawn location.

For an opt-in standalone visual capture, launch the project in the editor executable with `-game -KartFPCapture -ResX=1280 -ResY=720 -windowed`. It holds only the cosmetic input at center/left/right, saves `ue_center.png`, `ue_left.png`, `ue_right.png` into `Evidence/FirstPerson` and exits after 30 seconds. It never overrides gameplay steering or moves the pawn. This diagnostic mode is excluded from Shipping builds.

`Tools/import_first_person.py` imports only this new asset folder. `-FPFinishOnly` skips FBX import and saves materials/label/report. FBX import originally reported a reconstructed bind pose and missing smoothing groups; imported hand positions and rendered deformation must be checked, not inferred from successful import alone.

No existing kart/full-body Blender file, map, AI mesh, gameplay collision or physics was edited during creation of this setup. The latest V5 model and standalone kart are included alongside this setup for version control. Live two-machine/listen-server multiplayer and packaged-build testing are outside the completed local ownership checks.
