# Open central infield

Central group 09 scenery (including upgraded DV copies), pit/service pavement and its 22 parking markings are hidden in both DesertKarting maps. Starting-grid markings are retained in a separate filtered mesh. Existing ground collision remains; the subtle terrain infill adds no collision and stays outside the racing corridor. Tool chests and service tire stacks are removed from the visual map's instance placements. Source assets remain intact.

Restore a complete previous map from /Game/RoadToF1/Checkpoints/DesertKarting_BeforeOpenInfield or DesertKarting_Visual_BeforeOpenInfield. Evidence/DesertOpenInfield/restore.json records actor references. Hidden actors are in _Hidden_CentralPaddock. Original GLB/Blender and Source/Config are unmodified.

Scripts: desert_open_infield_author.py (Blender), desert_open_infield_apply.py (Unreal save), desert_open_infield_capture.py (live collision verification and screenshots). Terrain uses the existing per-map grass material to match adjacent infield. No new structures, gameplay changes or lighting changes.
