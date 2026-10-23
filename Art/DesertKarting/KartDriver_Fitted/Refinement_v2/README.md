# Kart driver seating refinement v2

Open `Kart_With_MakeHuman_Fitted_v2.blend` at frame 1. The MakeHuman body, original clothing and shoes, armature rest skeleton, and all original skin weights are retained. Mesh geometry is unchanged. The original fitted scene and original kart file are preserved.

The revised pose separates pelvic tilt from torso lean, brings the knees closer together, changes the ankle/foot alignment, and corrects finger contact around the wheel. The original outfit remains a casual garment; no racing suit, helmet, or material upgrade was started.

## Tank adjustment authorized by the user

Only the four existing `SK_Kart_Fuel_Tank_And_Cap_*` objects received a common transform. The tank assembly is uniformly scaled to **65.76%** of its original size and placed lower and forward between the legs. Its shell is approximately **204 × 302 × 197 mm**, with approximately **7.79 L external geometric volume**. This is not a measured internal usable fuel capacity. Commercial kart tank ranges include [8.5 L and 9.5 L products from KG](https://www.kgkarting.it/products/fuel-tanks/?lang=en) and [8.5 L OK/KZ tanks from OTK/Tony Kart](https://www.tonykart.com/parts_en.php?ID_categoria=21&ID_macrocategoria=2).

The selected transform was the closest candidate under the documented bounded search and clearance checks; it is not a proof of a global mathematical minimum. The final tank assembly has **no detected surface intersections with the driver or any other kart mesh**, including the steering and chassis. Tank parts retain their original meshes, materials, proportions, and relative assembly placement. All other kart object transforms are unchanged. The original fuel hose routing was retained and would need a separate mechanical connection review after relocation.

## Actual renders and comparisons

- `refined_front.png`, `refined_side.png`, `refined_top.png`, `refined_three_quarter.png`: final Blender Cycles renders.
- `comparison_front.png`, `comparison_side.png`, `comparison_top.png`, `comparison_three_quarter.png`: original fitted scene on the left, v2 on the right, rendered with matching cameras.
- `before_*.png`: genuine renders of the supplied fitted scene.

## Remaining fit limitations

**This is not a fully collision-free final fit.** The tank/lap conflict and hand/wheel-rim intersections are cleared. Residual garment intersections remain at the bucket seat, its raised grip ribs, and parts of the bodywork. Lower-leg/shoe contacts with the unchanged chassis crossmembers, front axle hardware, pedal supports, and hoses also remain. These are recorded explicitly in `validation_final.json`; no affected parts were hidden to make the renders appear clean.

The pelvis-support search uses glute landmarks against the actual seat sheet; a higher, visibly floating pose was rejected. Bone lengths are retained within floating-point tolerance. `validation_final.json` verifies exact mesh and skin-weight preservation, the unchanged rest skeleton, original source-file hash, and that only the authorized tank objects changed kart transforms. Its triangle-pair counts indicate surface intersections, not penetration depth or mechanical clearance certification.

No Unreal assets, gameplay, maps, gameplay collision geometry, original kart meshes, seat, steering wheel, or pedals were edited. No FBX export, push, or merge was performed. Work stops at the fit review stage.
