# Local cockpit wheel visibility revision

The V2 rim is closed (3360 rim vertices, zero boundary/nonmanifold edges). The wheel is about 0.59 m in front of the camera, beyond the 0.10 m engine near plane. Owner-only visibility does not selectively remove part of this static mesh. The apparent disappearance came from two separate causes: the raised, inward knee pose occluded the bottom rim, and the full-lock rim extended about 1.5% below the viewport at 105 degrees horizontal FOV.

## Changes

- Open only the separate POV knee bend planes to 42 degrees from the original rig rest pose. Hip/ankle transforms, leg lengths, all hand transforms, original topology, skin weights and bind skeleton remain unchanged. Re-bake all 49 steering poses.
- Change local eye FOV from 105 to 110 degrees. Eye height, pitch, wheel size, location, design, grip, dashboard and materials remain unchanged. At 16:9, the rim starts around 59–61% down the frame and retains about 3% margin at full lock.
- Add a 37 mm upper shaft connector of 9 mm radius to close the existing 20 mm hub/shaft gap in a separate cosmetic chassis copy. Other kart vertices and collision geometry are unchanged.
- Keep transient, nonreplicated, owner-only meshes. AI and remote players do not receive this POV setup.

## Files

Editable scene: `Kart_Cockpit_Wheel_Visibility_v3.blend`.

Exports: `Exports/SK_WV3_DriverPOV.fbx`, `Exports/SM_WV3_PlayerChassis.fbx`.

Unreal assets: `/Game/RoadToF1/PlayerVisuals/WheelVisibilityV3`. The wheel and materials continue to reference the unchanged V2 assets.

Genuine Unreal images and comparison: `Evidence/Wheel_Visibility_v3/After` and `Before_After_Steering.png` under the project root. Diagnostic captures use a stationary cosmetic rig/camera at measured straight and corner road locations; the gameplay pawn is not teleported. They demonstrate visual steering poses, not a dynamic driving or network test.

## Validation and limits

`validation.json` tests all 49 baked steering frames with deformed-surface overlaps, rim projection and line-of-sight probes. No wheel–leg intersections, arm–leg intersections, lower-rim knee occlusions or out-of-frame rim vertices were found. Expected glove contact obscures the grip areas. The near plane and visibility settings were not changed.

`Evidence/Wheel_Visibility_v3/animation_pose_check.json` compares compressed Unreal hand/knee/foot transforms against Blender samples. `tests.log` records the local ownership, steering and camera-restoration regression test.

**Remaining limitation:** the opened leg pose has offscreen outer garment contacts with the inherited seat/chassis (218 overlapping triangle pairs; this is not a penetration-depth measurement). This revision validates wheel visibility, not the entire seated character fit or photographic glove quality. The dashboard remains the existing cosmetic/static display.

Original Blender scenes and V2 Unreal assets are retained. For rollback, change the driver, steering animation and chassis soft references back to their V2 assets and change only the local FOV/test expectation from 110 to 105, then rebuild. `Backup` is a historical comparison, not a wholesale restore: other tasks have since added unrelated speed-view code to these shared files. No maps, lighting, physics, AI or gameplay sources are edited by this task. Other concurrent workspace changes are preserved. Nothing is committed, pushed or merged.

The editor build succeeded, imported compressed bone poses agreed with Blender within 0.00015 cm, and the steering/ownership test passed before the final cosmetic shaft reference change. An optional final repetition of that regression test was not executed: automatic approval review hit an account usage limit. The final actual Unreal captures and completed geometry checks include the connector.

Reproduce screenshots with UnrealEditor and the project/map arguments followed by `-game -ResX=1600 -ResY=900 -windowed -WheelVisibilityCapture`. The capture process exits after five screenshots.
