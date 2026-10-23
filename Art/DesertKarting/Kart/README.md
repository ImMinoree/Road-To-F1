# 125cc sprint kart reconstruction

Open `Kart_Reference.blend` in Blender 5.2 or later. The scene uses metric units, forward is +X, the wheelbase is approximately 1.11 m, overall length 2.04 m, and width 1.31 m. The model has separate named chassis, body, seat, engine, wheel, steering, brake, exhaust, and drivetrain components. Four Cycles renders are in `Renders/`.

`Exports/SM_Kart_Reference.fbx` is the Unreal import asset. In the open Unreal Editor, run `Tools/import_kart.py` from Tools > Execute Python Script to import the mesh parts and embedded material textures into `/Game/RoadToF1/DesertKarting/Kart`. It does not create or edit a level. The source `.blend` and 24 PBR texture maps are also included.

The current build is a detailed procedural base model, not a photorealistic production asset. The reference is a real kart photograph; matching that surface fidelity would require a professionally sculpted or scanned kart, calibrated tire/body materials, and hand-authored UVs and baked maps. Use this file as a structural/blockout base, or replace its body/engine/tire assets with a licensed high-quality kart kit or a photogrammetry/LiDAR scan, then retopologize and bake maps for UE5.

Rebuild with `D:\Boring\blender.exe -b build_kart.py` from this directory. The build script recreates the Blender file, FBX, texture maps, renders, and manifest.
