# Editable racer outfit study — V4 (partial, realism target not achieved)

Open `Kart_With_MakeHuman_Racer_v4.blend`. This is a separate scene based on
`../Refinement_v3/Kart_With_MakeHuman_Fitted_v3.blend`. Previous versions are preserved.

## What changed

- Separate fitted one-piece outfit adapted from the installed MakeHuman work-suit topology, with long anatomical sleeves, sewn-on red/white panels, a zipper placket, geometric seams, cuffs and a neck underlayer.
- Gloves derived from the existing MakeHuman hand topology, retaining finger weights. Separate boots derive from the existing high-top shoes and include geometric lacing.
- A custom profiled full-face helmet: open visor aperture, separate curved smoked lens, chin bar, trim, hinges, vents, neck padding and lacquer graphic meshes. It is not a sphere or a 2D image.
- Packed UV fabric normal and roughness tiles, also available in `textures/`. Fabric, leather, rubber, polycarbonate, paint and metal have separate editable shaders. These are Blender materials, not a completed Unreal material package.
- The source fitted action is preserved. A separate V4 action contains the grip changes. The reclined torso and feet retain the fitted pose.

The original human mesh vertices, original human weights, skeleton rest hierarchy,
kart geometry/transforms (including the refined tank), and original light objects
were checked against saved hashes. Original casual clothes and shoes remain in the
new scene, hidden. The kart, track, Unreal assets and gameplay were not edited.

## Actual inspection output

- `racer_front.png`, `racer_side.png`, `racer_rear.png`, `racer_three_quarter.png`: genuine Blender Cycles renders using the unchanged scene lighting.
- `geometry_solid.png`: untextured Workbench geometry inspection. The scene opens with material-preview shading selected; this is not evidence of a separate interactive viewport quality review.
- `views_contact_sheet.png`: the four rendered views together.
- `reference_comparison.png`: supplied reference beside the actual modeled result.
- `validation.json`, `grip_validation.json`, `preservation.json`: diagnostics, not artistic-quality certification.

## Quality assessment against the reference

**The requested photorealistic/professional production quality has NOT been achieved.**
The colors and full-face equipment are present as actual rigged geometry, but the
work-suit base still reads as a procedural garment conversion. Shoulder/armhole
transitions, chest-panel edges, collar coverage, cloth tension and compression
folds remain insufficient. The source pose is stiff at the arms and high at the
knees compared with the reference. Gloves lack convincing sewn finger structure;
the boots are adapted shoes rather than a faithfully modeled kart boot. The
helmet needs better chin/visor proportions, flush graphic boundaries, ventilation
construction and manually authored surface wear. The outfit remains too smooth
and simple to match the reference. More polygons or a flattering render would
not resolve those shape and construction issues.

Unresolved fit issues include glove **and underlying hand** overlap with the
steering-wheel rim; garment intersections with seat/bodywork/control-frame/hoses;
boot intersections with chassis/axle/pedal frame; and head/helmet or neck-padding
surface contacts. Full support against the seat back is still imperfect.
No tank intersections were detected by the surface-pair test. That test cannot
prove volumetric clearance and counts triangle pairs, not penetration depth.
See `validation.json` for the exact current counts. Do not treat this scene as
collision-free or gameplay-ready.

All new outfit parts are bound to the existing armature and all inspected vertices
have weights. Temporary +/-8 degree steering articulation tests produced finite
meshes, but one arm's target was unreachable on each side with the current fixed
recline/reach. Therefore steering contact and deformation quality are **not
validated**. Source animations are retained; a finished steering/pedal animation
system was not supplied. Nothing was imported into Unreal or exported as a final
production asset in this pass.

## Work needed to reach the target

Use this as an editable blocking/tailoring base. A character artist needs to fit
the shoulders/arms and control reach together, build a properly patterned racing
suit around this human (cloth simulation plus manual sculpting in the seated pose),
retopologize its joints and panels, sculpt glove/boot construction and helmet
details, correct intersections, and bake high-resolution normal/AO/roughness maps.
Then validate contact/deformation over the complete steering and pedal range.
This can be done in Blender without purchasing marketplace assets.

## Local asset provenance

The installed `male_worksuit01.mhpxy` embeds **CC0**, author **MakeHuman Team**,
copyright `(c) www.makehumancommunity.org 2001-2020`. The license metadata is copied
into `preservation.json`; the garment was loaded locally, with no asset downloads
or purchases. Gloves use the user's existing MakeHuman human, and boots use the
existing shoes05. New helmet and outfit details were authored by the accompanying
Blender scripts. The MakeHuman application itself has a different software license;
the CC0 claim here applies to the asset metadata, not the application code.

No push or merge was performed.
