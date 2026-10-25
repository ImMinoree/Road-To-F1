# Reference-inspired local cockpit v2

Open `Kart_Cockpit_Reference_v2.blend`. This is a separate editable 3D scene, not a replacement of the original kart or full-body driver. The `Exports` folder contains a standalone rigged POV FBX, steering-wheel FBX and cosmetic chassis FBX. Unreal assets are in `/Game/RoadToF1/PlayerVisuals/CockpitReferenceV2`.

The ranked image comparison and image-supported findings versus modeling assumptions are in `ANALYSIS.md`.

## What changed

- Replaced the local 402 mm circular wheel and projecting T-shaped center with a 335 mm contoured wheel: flattened bridge/lower outline, 34 mm blue padded grips, real split metal spokes, six recessed fasteners, lower metal crossbar and a modeled LCD logger with buttons and LEDs. Display text is actual geometry and explicitly says DEMO; it is not live telemetry.
- Retained the existing anatomical MakeHuman glove topology and skinning, refitted wrist orientations and solved the two arm segments with fixed lengths. Red gauntlets have narrower wrist fit, with dark sleeves, existing sewn edging and raised glove panels.
- Added a separate skinned copy of the existing lower suit/boots so the knees are visible. Knees were rotated inward 21 degrees about the fixed hip-to-ankle lines, preserving hip/foot positions and segment lengths. Local garment width corrections reduce excess knee/inner-thigh cloth. Original full-body assets and weights were not edited.
- Corrected the local wheel/shaft relationship in a separate chassis copy. The steering shaft is slender and no longer protrudes in front of the hub. No physics/collision geometry changed.
- Driver eye: (5, 0, 105) cm from the source kart-ground origin, 105-degree horizontal FOV and 10-degree downward pitch. Everything remains at physical centimeter scale; the cockpit was not shrunk to create space. The owner camera is restored when cockpit view is disabled.

## Validation

Actual Unreal 5.8.3 1600x900 captures were visually inspected at center and +/-25-degree steering, on straight and corner road samples. Raw images are in `Evidence/Cockpit_Reference_v2/Before` and `After`. `Before_After_Reference.png`, `Corner_Before_After_Reference.png` and `Unreal_Views.png` compare the real outputs. The real photo informs geometry rather than fixing the camera composition.

These are **stationary diagnostic POV samples in the real Unreal map**, not a claim of a completed driving-dynamics test. The diagnostic camera and cosmetic rig move to the sampled road positions; the gameplay pawn, race system and physics are not teleported or controlled by this tool.

Projection checks put the uppermost driver/wheel geometry at 61.7% screen height centered and 60.0% at full lock. The upper roughly 60% remains clear of cockpit geometry, and the inspected corner apex and track remain visible. Knees are visible below the hands; tank/front-wheel detail is less prominent than in the downward-looking photo because the road view is prioritized.

Checks across 49 poses found zero evaluated triangle surface crossings for arms versus legs, arms versus chassis, legs versus chassis and left versus right legs. These are surface checks, not a signed-volume or cloth simulation proof. The contoured-grip vertex check still finds up to 0.68 mm of glove/rim overlap, a submillimeter contact imperfection; no sampled glove vertex penetrates by more than 3 mm. Minimum elbow bend is about 56.6 degrees; wrist solve error is below 0.001 mm. Do not interpret triangle counts or solver accuracy as a photorealism rating.

`animation_pose_check.json` in Evidence compares compressed Unreal hand, knee and foot positions against Blender at five steering samples. This caught a stale knee clip retained by mesh reimport; the importer now explicitly reimports the baked animation. The corrected clip must be used with the new mesh. Unreal ownership, tilted-wheel alignment, camera restoration and source hand-position automation checks also passed.

## Ownership and reversibility

The native `ULocalKartDriverVisuals` component retains its local-player/ULocalPlayer eligibility gate, `OnlyOwnerSee`, zero collision, no replicated cosmetics, and the optional third-person `OwnerNoSee` hook. AI, dedicated servers and remote-player pawns do not create these meshes. No gameplay depends on the visual rig. A live network session and packaged cook were not tested.

Restart an already-open editor to load rebuilt native code. `Tools/PreviewCockpitV2.ps1` launches a separate player preview. `-Legacy` uses the original assets and original eye view. The component's `bReferenceCockpit=false` property is another revert option **before** the local visuals are created. Prior source files are retained under `Backup`; avoid blindly restoring shared source files over unrelated concurrent edits.

This workflow did not save maps, alter track/lighting actors, edit physics/AI/race-start code or modify the source V5/FirstPerson Blender files. Another concurrent workspace task changed the two map hashes during the work; those edits were left untouched. Initial and capture-time hashes are recorded in Evidence, so this report does not claim that the entire shared workspace stayed unchanged. No commit, push or merge was performed for this cockpit revision.

## Remaining visual differences

Glove finger articulation, cuff edge finish, suit folds and material variation still need manual sculpting/tailoring to approach the photographic reference. This is a genuine geometry and framing improvement, not a finished photorealistic cockpit. Logger shape/branding is generic and its readings are a static DEMO. The current source lower-body proportions remain inherited from the fitted model; the full-body third-person driver was not redesigned.

Reproduce using `build_cockpit.py`, then `Tools/import_cockpit_v2.py`. `finish_cloth_clearance.py` records the incremental last cloth correction; a full fresh build already includes it, so do not apply it twice. Use `validate_geometry.py`, `check_surface_contacts.py`, `Tools/validate_cockpit_v2_animation.py` and the Unreal automation test for validation. `Tools/compare_cockpit_v2.py` composes evidence without retouching the raw images.
