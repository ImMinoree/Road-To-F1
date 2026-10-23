# Infield grass

Original seeded Blender geometry, authored for this project; no downloaded textures or marketplace assets.

`InfieldGrass.blend` contains three reusable clumps, each with 56 curved tapered blades / 336 triangles. Blades are 10–22 cm tall before the scatter's 0.8–1.25 scale variation. Vertex-color red runs from zero at the root to one at the tip for shading and wind anchoring. These are mesh blades inspired by the reference's hair appearance, not a transferred Blender hair simulation.

`Tools/desert_grass_author.py` reads the existing lawn FBX surfaces and the verified route. It creates a seeded, irregular scatter with a conservative 7.5 m centerline exclusion and five footprint probes against the actual asphalt, curbs and runoff meshes; no asphalt geometry is modified. Adjust spacing, height range, blade width or count in that source and regenerate to change the look. Export units are metres; Unreal FBX import converts to centimetres.

Unreal content: `/Game/RoadToF1/InfieldGrass`. `M_InfieldGrass` exposes RootColor, TipColor, Transmission, Roughness, WindSpeed and WindAmplitudeCm. Wind is root-anchored material vertex motion, not Blender turbulence physics. Defaults are 2.2 cm amplitude and 1.25 speed. The material uses opaque two-sided blades and foliage subsurface shading; no transparent grass cards.

Three shared foliage types instance the clumps in both DesertKarting maps. Cull distances are 50–75 m; grass collision and dynamic grass shadows are disabled. This is a bounded desktop foliage pass, not a measured 20-kart performance claim.

Recovery: maps are checkpointed as `/Game/RoadToF1/Checkpoints/DesertKarting_BeforeInfieldGrass` and `DesertKarting_Visual_BeforeInfieldGrass`. To remove only grass while keeping later map edits, use Foliage Mode to remove instances of the three types under `InfieldGrass/Foliage`. Keep assets for later reuse. Re-running the importer replaces only these foliage types' instances.
