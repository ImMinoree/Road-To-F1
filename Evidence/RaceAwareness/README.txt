Rear view and nearby-opponent awareness
=====================================
Open /Game/RoadToF1/Maps/DesertKarting_Visual and Play.
Hold C: look back. Release: restore the currently selected first/third-person camera.
F2: toggle the live rear mirror. V and M keep their existing camera/map controls.

The top-center strip is a horizontally reflected live rear scene, not a static image.
The lower-right radar has been removed. A lower-left full-circuit outline shows the player as a red dot and all opponents as white dots.
Close-kart arrows appear within 9 metres. White = nearby, amber = projected close approach within 1.5 seconds,
red = close overlap or projected collision within 0.8 seconds.
Screen-edge chevrons indicate nearby-kart direction relative to the kart's forward heading.
Warnings persist briefly and fade to reduce threshold flicker.
Route-distance and elevation filters reduce alerts from separate nearby track branches.
These are proximity aids, not guaranteed collision predictions: opponents can change direction.

One local-player scene capture: 640x160, maximum 20 Hz (MirrorHz editable on HUD component).
Capture stops while mirror disabled, looking back, or viewing the full-screen map.
No capture components are created on AI karts. No new map assets or opponent actors.
The full-screen rear camera is attached to the player's kart and does not change its rotation.

Implementation: KartRaceAwareness.h/.cpp and KartRaceAwarenessMath.h, hosted by the existing
RaceStartHUD. Existing physics, race gate, AI, navigation and cockpit assets are reused.
KartMechanicalVisuals.cpp only renames the Folder asset-path constant to avoid a unity-build
name collision with existing source files. Checkpoint contains pre-change HUD/source files.

Validation: build_final.log; Automation/index.json; pie_result.json; unreal_final.log.
PIE validation invokes the same bound component actions via Unreal Python; OS keyboard input
was not synthesized. Existing AI karts are repositioned only inside the unsaved PIE world to
exercise close-side and rear visibility. Screenshots are actual PIE renders.
The test checks mirror capture, both camera-mode restorations, radar tracking, disabling
capture, full-map interaction, render-rate ceiling, and unchanged saved map/route hashes.
Automation checks overlap, approaching/receding traffic, range, elevation and route filtering.
No comparative GPU benchmark or long race session was performed.

