# Kart driver procedural build

Created with Blender 5.2.2 from the existing `Kart_Reference.blend`. The source kart file was read-only during the build and remains unchanged. Units are metres, +X is forward, and the fitted controls use the measured steering center `(0.62, 0, 0.70)` and pedal region around `(0.53, ±0.14, 0.15)`.

## Deliverables

- `Kart_With_Driver.blend` — the original kart scene plus the fitted driver.
- `Kart_Driver_Rig.blend` — editable standalone driver, rig, controls, animation and procedural materials.
- `Kart_Driver_UE58.fbx` — skeletal mesh and baked driving animation. Reimport validation in Blender 5.2.2 found 1 armature, 74 bones, 105 mesh objects (80 skinned), and the `Driving_Steer_Pedals_48f` action.
- `Renders/` — four genuine Cycles renders from the combined scene.
- `AnimationPreview/` — 48 rendered EEVEE frames. Open `AnimationPreview/preview.html` in a browser and press Play.
- `Import_Kart_Driver.py` — Unreal Editor Python import helper.
- `driver_manifest.json` — machine-readable fit and build validation.
- `build_driver.py` — reproducible Blender Python generator.

## Blender

Open either `.blend` file in Blender. The combined scene retains the kart; the standalone scene contains only the driver and its controls. The rig has 63 deform bones plus non-deforming root and IK/pole controls. Driver meshes have armature modifiers and vertex groups. The `Driving_Steer_Pedals_48f` action covers frames 1–49; steering-wheel and hand targets are parented to the wheel pivot, foot IK targets are animated, and the head/upper torso have subtle cornering keys.

## Unreal Engine 5.8.3

1. Enable **Python Editor Script Plugin** if it is not already enabled, then restart the editor.
2. Open the project and run `Import_Kart_Driver.py` from the Unreal Python console or Output Log (`py "<full path to Import_Kart_Driver.py>"`). It imports to `/Game/RoadToF1/DesertKarting/KartDriver` without changing a level or gameplay asset.
3. In the Content Browser, open the imported skeletal mesh and its `Driving_Steer_Pedals_48f` animation sequence (the importer may suffix take names). Press Play in the animation editor to test the baked steering/head motion. The foot and hand IK helper controls are Blender rig controls; Unreal receives the baked skeletal animation, not Blender constraints.
4. For gameplay, attach the skeletal mesh to the kart and use the imported sequence as a preview. Recreate interactive steering/pedal response in an Anim Blueprint or Control Rig; the preview is a short authored test, not a complete gameplay animation system.

## Quality and limitations

This is an editable procedural fit/rig prototype, not a photoreal human asset. The new continuous suit remesh reduces the visibly segmented body, but the render remains stylized: arms and legs read as smooth lofts, hands are simplified, cloth detail is shader bump rather than authored texture maps, and the helmet is a modeled shell with a dark visor. It does not reach the reference's anatomy, tailored clothing, or material microdetail. The FBX has been reimported into Blender and its armature, skinned meshes, and animation action were verified; Unreal Editor itself was not available for an import test. Treat the Unreal import helper as a starting point. A convincing final result needs a high-quality sculpted human base, carefully retopologized and UV-unwrapped, authored or scanned fabric/helmet textures, and artist-reviewed skinning; procedural modeling alone did not meet that bar here.

Blender on this machine was built without FFmpeg encoding, so the animation preview is a rendered PNG sequence with a browser player rather than MP4.
