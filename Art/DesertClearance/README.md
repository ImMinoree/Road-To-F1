# Desert track clearance

Both DesertKarting maps use filtered copies of the timing/pit-furniture meshes. Removed: 13 pit-sign bases, boards and posts, visual replacement pods, and the booth at Unreal (-4500,-2000) cm. The other two booths and start gantry remain.

Original Blender, GLB and imported mesh assets are retained. Restore the complete previous level from /Game/RoadToF1/Checkpoints/DesertKarting_BeforeClearance or DesertKarting_Visual_BeforeClearance. Evidence/DesertClearance/restore.json records original per-actor mesh references and collision settings for selective restoration.

Authoring: Tools/desert_clearance_author.py. Apply: Tools/desert_clearance_apply.py. Capture: Tools/desert_clearance_capture.py with -ClearanceAfter. Live collision verification: Tools/desert_clearance_verify.py.
