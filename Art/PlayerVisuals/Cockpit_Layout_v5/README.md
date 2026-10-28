# Local-player cockpit layout V5

Editable scene: `Kart_Cockpit_Layout_v5.blend`. Rigged FBX, static wheel and cosmetic chassis are in `Exports/`; runtime assets are in `/Game/RoadToF1/PlayerVisuals/CockpitLayoutV5`.

The reference shows knees beneath the wheel, visible front slicks outside the arms, and a low exposed front chassis. The previous view hid those parts with an upright, high seating layout and widely spread knees. V5 refits the existing MakeHuman pose, keeps the same skeleton/weights, and bakes the existing 49-frame +/-25 degree steering action with retained hand contact. Both feet are refitted to the cosmetic pedals. A final 100 mm pedal/foot drop keeps the boots beneath the wheel; the nose and front linkage are reshaped around that clearance.

The local cosmetic seat, steering assembly and driver eye have been lowered together. Final eye: source `(0.05,0,0.75)` metres; wheel centre `(0.62,0,0.52)` metres; horizontal FOV 95 degrees and pitch -10 degrees. The closed 335 mm wheel is unchanged in size. The front track is 1.31 m between tire centres; the existing wheelbase remains 1.11 m. The local front assembly and nose are refitted to provide visible tires, hubs, frame and knees. This is a dedicated first-person visual layout, not an update to gameplay wheel/collision positions or the third-person kart.

Two genuine inherited surface defects were fixed: front slick tread/sidewall shells had inward-facing normals, and the lower suit/boots had their authored fabric UVs on an inactive joined channel. V5 corrects face orientation and restores those existing UVs in the primary channel. Materials are reused from CockpitTargetV4; world lighting is unchanged. The cosmetic fuel-tank assembly is proportionally reduced to 65% and moved forward/down to clear the lowered lap. Original kart and full-body scenes are untouched.

`validation.json` checks the complete rim through all 49 steering frames and samples leg occlusion at nine poses. `arm_leg_checks.json` records geometric arm/leg checks at nine poses. `contacts.json` records residual leg/chassis surface contacts at centre and both steering extremes; these include remaining seat/garment, rear frame and boot/front-linkage contacts. The seat-clearance projection experiment was rejected because it worsened the surface test; its deformation is not in the final scene. This is not a whole-body intersection-free certification.

Actual Unreal evidence belongs in `Evidence/Cockpit_Layout_v5/After`, including centre, left, right and two corner samples. These are visual diagnostic captures at fixed road positions; they do not move the physics pawn or certify dynamic driving/multiplayer. The existing ownership regression tests check local-player-only components, remote/AI exclusion, imported grip transforms and camera restoration. All cosmetic meshes remain nonreplicated, owner-only and collision-free.

The target is not fully matched: tailored knee folds, glove/cuff construction, front-bodywork styling and material response still need manual finishing. The inherited high-density POV has no authored LODs. No claim of photorealism or perfect full-body fit is made.

For rollback, preserve unrelated project changes and restore only this task's visual asset paths and camera/wheel values from `Evidence/Cockpit_Layout_v5/SourceBackup`. All V4 assets remain. Do not wholesale restore old source backups over concurrent work. No push or merge was performed by this task.

Final evidence: runtime_verified.log and tests_retry.log in Evidence/Cockpit_Layout_v5. The comparison PNG combines unchanged V4 before images, actual V5 Unreal captures and the supplied target. No generated cockpit imagery is substituted.


The final ownership/steering test retry completed successfully. The initial final test process exited without a result; tests_retry.log is the authoritative final test record.

