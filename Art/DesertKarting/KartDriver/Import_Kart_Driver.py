"""Import the generated kart-driver FBX into the currently open Unreal project.

Run in Unreal Editor with Python Editor Script Plugin enabled.
"""
import os
import unreal

fbx_path = os.path.join(
    unreal.Paths.project_dir(),
    "Art", "DesertKarting", "KartDriver", "Kart_Driver_UE58.fbx",
)
destination = "/Game/RoadToF1/DesertKarting/KartDriver"

if not os.path.isfile(fbx_path):
    raise FileNotFoundError("Kart-driver FBX not found: " + fbx_path)

options = unreal.FbxImportUI()
options.import_as_skeletal = True
options.import_mesh = True
options.import_animations = True
options.import_materials = True
options.import_textures = True
options.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH

task = unreal.AssetImportTask()
task.filename = fbx_path
task.destination_path = destination
task.automated = True
task.replace_existing = True
task.save = True
task.options = options

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
print("Kart driver import complete:", task.imported_object_paths)
print("Open the Skeletal Mesh and imported animation sequence in the Content Browser to preview.")
