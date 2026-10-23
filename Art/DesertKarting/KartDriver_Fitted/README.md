# MakeHuman kart seating inspection

Open `Kart_With_MakeHuman_Fitted.blend` in Blender 5.2 or later. `front.png`, `side.png`, and `three_quarter.png` are actual Cycles renders of that scene, with the supplied clothing and materials retained.

## What was preserved and repaired

- The original kart component meshes, transforms, and materials are unchanged. Neither source `.blend` was overwritten; SHA-256 checks are recorded in `fit_validation.json`.
- The character comes from `Art/HumanBase/KartDriver_Base.blend`, with its original body, clothing, shoes, eyes, and named MakeHuman armature. No replacement mannequin or newly modelled body was used.
- The supplied `.blend` had no skin weights or armature modifier on its body, clothing, and shoes, and its armature orientation did not match the meshes. The companion `KartDriver_Rigged.fbx` contains the same vertices and the original MakeHuman weights. These were restored by verified vertex correspondence, retaining the `.blend` meshes and materials.
- Character scale is uniform, approximately 1.80 m standing stature. The body and skeleton have separate source-axis corrections. Kart coordinates remain metres, +X forward, +Z up.
- Bone hierarchy and lengths are retained. The seated pose has a mildly reclined torso, forward gaze, bent elbows and knees, opposed thumbs and curled fingers at the wheel, and feet aligned to the pedal area. Source custom normals were cleared in the fitted copy where they caused visible faceting artifacts.
- The new action `Kart | seated fit inspection` stores the pose at frame 1. This is a static fit inspection; no steering or pedal animation system was added or Unreal import performed.

## Remaining limitations — fit is incomplete

The original kart fuel tank extends approximately X -0.04 to 0.27 m, Y -0.23 to 0.23 m, Z 0.44 to 0.74 m. It occupies part of the seated lap region. The original casual garment intersects this tank and parts of the bucket seat; this has not been hidden or removed. A separate seating/tank layout review and garment corrective work are needed before claiming a collision-free fit.

The original coarse hand and garment skinning also needs manual contact/deformation refinement: some finger/rim and garment/control surface intersections remain. The shoes have been positioned at pedal height and outside the upright pedal supports. Clothing and skin weights were preserved rather than silently reshaped to conceal these problems.

`contact_check.json` records evaluated-mesh triangle surface intersections. These counts are diagnostic, not penetration-depth estimates or proof against enclosed-volume intersections. `fit_validation.json` records target reach errors, source file hashes, binding correspondence, and kart geometry/transform checks. `check_fit.py` can reproduce the surface checks. `fit_driver.py` reproduces the separate scene and renders without saving to either source file.

No Unreal gameplay, maps, original kart or human files were changed. No push, merge, FBX export, or Unreal import was performed.
