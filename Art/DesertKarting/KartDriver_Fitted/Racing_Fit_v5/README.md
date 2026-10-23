# V5 — seated fit and steering IK

Open **Kart_With_MakeHuman_Racer_v5.blend**. The scene opens at centered steering,
frame 25. V4 and all earlier files remain unchanged.

## Using the rig

- Play frames **1–49**: frame 1 = left **−25°**, frame 25 = center, frame 49 = right **+25°**.
- Select `V5 | STEERING - degrees` and edit its `steering_deg` custom property after disabling its preview action if you want to control it manually. The supported/tested interval is −25° to +25°.
- Wrist targets follow the wheel controller. Two-bone arm IK has stretching disabled; elbow pole targets control bend direction. Small clavicle movements accommodate the lowered hand rather than stretching an arm.
- The original MakeHuman skeleton, rest bone hierarchy and all original skin weights are retained. No human, kart, suit, helmet, glove or boot was rebuilt/replaced. Original source actions are retained, with a separate V5 action and preview control animation.

The wheel's original rim/hub/spoke mesh components articulate through Hook modifiers.
The original rest mesh geometry/transforms remain unchanged. The steering shaft,
chassis, tank, seat, pedals, hoses and front wheels are fixed. This is a **driver
steering preview**, not a vehicle steering/linkage simulation. It does not establish
the kart's mechanical lock or a gameplay steering range.

## Fit changes

The grip uses the actual rim center `(0.62, 0, 0.70 m)`, radius **184 mm**, and
tube radius **17 mm**. The wrists, elbows, shoulders, fingers and opposed thumbs
were posed around that surface. A small glove clearance shape key, at most
1.1 mm in its center-pose correction, removes remaining surface overlap.

The feet use a heel-up/toe-out pedal pose to clear the original frame and tank.
Sampled pedal-top/boot separation is approximately **1.4–1.7 mm**. The reclined
torso, pelvis and natural forward head alignment are retained. Trouser shape keys
narrow the loose lower legs, tuck their hems, and clear the seat, raised ribs and
hoses. Separate decorative panels conform to the fitted suit so they do not hover
above its changed shape. These are editable corrections; original garment mesh
vertices and weights are preserved beneath the shape keys/modifiers.

## Checks and actual images

`validation_final.json` records checks at **49 poses** across the configured range,
using actual render subdivision:

| Check | Result |
|---|---|
| Unreachable wrist targets | None in the tested range |
| Maximum wrist position error | 0.00047 mm |
| Maximum arm length change | 0.00026 mm; stretch disabled |
| Elbow bend | At least 26.4° |
| Hand/glove vs rim surface intersections | Zero in all 49 samples |
| Worst analytic rim penetration | Zero detected |
| Maximum nearest hand/rim gap | About 1.05 mm |
| Complete visible driver/outfit vs kart | Zero surface-pair intersections at left, center and right |
| Original V4 source file / protected weights, rest rig, kart and lights | Unchanged |

The requested genuine Cycles images are `steering_center.png`, `steering_left.png`,
`steering_right.png`, `side.png` and `three_quarter.png`. `grip_center.png`,
`grip_left.png` and `grip_right.png` provide closer contact inspections.
`V5_Review.png` combines the requested views and a grip close-up;
`V5_Grip_Review.png` shows all three grips; `V4_V5_side_comparison.png` compares
the original and fitted pose using the same camera and lighting.

The actual final views and grip close-ups were visually inspected. Both hands
retain a believable grip at left/center/right with bent elbows and no visible
significant rim penetration. Steering is validated **only for the tested ±25°
range**, together with the recorded geometric checks; this is not full character
or mechanical-lock approval.

## Remaining limitations

- The **existing V4 helmet shell/head and neck-padding intersections remain**:
  122 shell/head and 380 padding/body triangle pairs at the render subdivision.
  These are internal character/gear contacts, separate from the cleared kart
  contacts; penetration depth has not been certified. The full character is not
  claimed to be completely intersection-free.
- Full upper-back contact/support remains imperfect in the original seat. The
  current reclined torso/pelvis arrangement was preserved, rather than changing
  the kart or reshaping the human.
- V4 garment construction, shoulder transitions, visible seams, helmet detail
  and material realism are retained limitations. This pass does not claim
  photorealism or complete anatomical/garment production approval.
- Surface-pair checks do not prove volumetric clearance or simulate compressible
  glove/fabric contact. The render views must be considered alongside the numbers.
- Validation covers **±25° only**. A wider lock needs further shoulder/body and
  wrist articulation work and another contact sweep. Blender constraints need
  baking before any future game-engine skeletal export.

No Unreal assets, maps or gameplay were modified. No push or merge was performed.
