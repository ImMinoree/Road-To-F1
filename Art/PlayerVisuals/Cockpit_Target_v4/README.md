# Cockpit target revision V4

Separate editable scene: `Kart_Cockpit_Target_v4.blend`. Original V3, full-body driver, original kart, maps and gameplay files are retained.

## Reference comparison and changes

The supplied target has a larger, blue padded wheel with a compact three-spoke metal center, a readable logger, red textile gloves with piping, darker woven sleeves, and more visible seated body/front-wheel context. These are more significant than adding camera shake.

This revision retains the exact closed 335 mm rim and the existing steering grips/53-bone rig/49-frame animation. It replaces the internal spokes with beveled stamped plates and an actual slotted lower spoke, adds recessed hub hardware, and creates a 145 mm modeled logger housing, bezel, inset UV-mapped screen and nine indicator lenses. The lower rim now uses the same blue suede as the upper grip. It does not scale the whole kart or wheel to force a match.

The existing MakeHuman glove/sleeve topology is refined with subdivision, small modeled fabric folds, projected raised glove piping and stitches. The bind hierarchy and animation are retained, with subdivision interpolating skin weights. Woven base-color, roughness and tangent-normal textures accompany the geometry. This is a real skinned mesh, not a generated cockpit image.

Original kart vertex positions are retained. The prior local copy had collapsed most source material categories into rubber. V4 restores alloy, frame, tire, body, seat and tank distinctions and reuses existing locally authored kart PBR maps. No new lighting is added.

The final eye is 1.05 m above ground, above the 0.925 m shoulders, at source X=0.05 m. Horizontal FOV is 95 degrees and pitch is -22 degrees. A lower eye trial was rejected because it placed the camera below the shoulders. The steering wheel stays within frame at full lock, with about 12% minimum bottom clearance at 16:9.

## Runtime

Assets: `/Game/RoadToF1/PlayerVisuals/CockpitTargetV4`. Source integration is confined to `LocalKartDriverVisuals` and its existing regression test. Meshes and the two new 3D text readouts are transient, collision-free, nonreplicated and owner-only. AI/remote full-body visuals are unchanged.

Speed uses the local pawn's actual cm/s converted to km/h. TIME uses the existing race elapsed getter when a local authoritative game mode is available; otherwise it shows local session time. It is not a multiplayer-synchronized lap clock. The fixed `1` represents direct drive, not a new gearbox. The load bar and indicator lenses are decorative; no engine RPM signal is invented. The dashboard does not control gameplay.

## Validation and limitations

`validation.json`: full 49-frame rim framing and closed topology checks, plus knee-occlusion probes at nine steering poses. These are not signed-volume or full-body cloth simulation tests. The inherited offscreen garment/seat contacts remain outside this wheel-focused validation.

The editor build succeeded. `Evidence/Cockpit_Target_v4/tests.log` records a passing ownership/steering regression test, including imported compressed hand poses and restoration of the original camera. There are no zero-area faces in the refined driver source mesh. FBX emitted a recreated-bind-pose warning and tangent warnings on UV-degenerate detail surfaces; the imported bone checks passed. The wheel's closed hard-surface shells were given outward normals before the final import.

Actual Unreal screenshots, comparison and regression log are under `Evidence/Cockpit_Target_v4` at the project root. Diagnostic captures show center and +/-25 degree steering on straight/corner road samples using only a cosmetic camera/rig; they do not teleport the physics pawn or certify dynamic multiplayer driving.

This is a reference-inspired improvement, not a claim of matching the supplied image's photorealism. The glove anatomy, cuff cut, tailored wrinkles and material response still need manual character-art finishing to equal that reference. The inherited kart layout also places the front tires/body differently in the view. The detailed POV mesh has no authored LODs and still needs performance optimization for a shipping asset.

A closer-knee leg fit was tested independently but rejected because it introduced fairing intersections. `Leg_Fit_Candidate.blend` and its trial scripts/results are experiments only and are not imported or used at runtime. The active scene retains the previously verified leg pose and original cosmetic pedal placement. Matching the reference's knee/tire context properly needs a deliberate seat/pedal/bodywork refit, followed by full collision and posture validation; it is not solved by adding polygons or simply forcing those limbs into the screenshot.

## Reproduction and rollback

Art scripts in order: `make_textures.py`, `build_target.py`, `finish_surfaces.py`, `save_final_camera.py`, `fix_wheel_normals.py`, `finish_material_response.py`, `validate_target.py`; then `Tools/import_cockpit_target_v4.py`. `Tools/finish_cockpit_target_v4.py` reimports only a later wheel-normal correction, and `Tools/finish_cockpit_target_materials.py` applies the final coated satin-alloy response and real LCD backlight. Captures: run the project and DesertKarting_Visual map with `-game -ResX=1600 -ResY=900 -windowed -CockpitTargetCapture`. The diagnostic process exits after five shots. Wait for first-use materials to compile before judging the result; the final evidence uses loaded materials.

To restore V3, point the local driver/animation/chassis to WheelVisibilityV3, the wheel to CockpitReferenceV2, restore FOV 110 and eye transform `(5,0,74)` / pitch -10, and remove the V4 dashboard readouts. Preserve unrelated speed-view code. Do not wholesale restore old source backups over concurrent changes.

No paid assets were purchased, and no changes were pushed or merged.
