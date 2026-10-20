# RoadToF1-Realism

Independent Unreal 5.8.3 C++ project. **Visual milestone is not accepted.** This is the playable foundation permitted by available verified assets. No original project files, old circuit geometry, race code or stylized hero assets were copied.

Open `RoadToF1-Realism.uproject` in installed Unreal 5.8.3, open `/Game/RoadToF1/Maps/VisualProof`, press Play, click viewport. W accelerates, S brakes/reverses, A/D steer, R resets, Escape exits PIE. No finished kart or driver is represented. Temporary swept kinematic pawn is capped at 57.6 km/h; road-following trace and a sphere provide basic movement only. It does not reproduce kart physics.

`Tools/Open.ps1 -Profile Balanced` launches the game at 1920×1080, High scalability (2), 75% internal resolution, conventional shadows. `-Profile Validation` selects Epic (3), VSM and 100% internal resolution. TSR and software Lumen are configured; hardware ray tracing is disabled. No Nanite forced onto the small road meshes. Manual daylight exposure is held constant. No motion blur, bloom, grain or artificial sharpening added.

Reproduce geometry with `D:\Boring\blender.exe -b -t 4 --python Tools/model_proof.py`. The `.blend` uses metres; FBX exports are individually imported in centimetres, with longitudinal UV repeat every 2 m. Rebuild level using UnrealEditor-Cmd with `-run=pythonscript -script=<absolute Tools/build_scene.py> -nullrhi -unattended`. This intentionally replaces only this project's VisualProof map. Rendering validation must use a real RHI, never NullRHI.

Capture using UnrealEditor.exe with `-ExecCmds="py <absolute Tools/capture_scene.py>" -unattended -nosplash`. Three fixed 1920×1080 views are saved under Evidence after settling. The capture script exits its own editor. Do not invoke against another editor with unsaved work.

Runtime bounded test: UnrealEditor.exe `<absolute uproject>` `/Game/RoadToF1/Maps/VisualProof` `-game -windowed -ResX=1920 -ResY=1080 -ProofSmokeTest -unattended`. This automatically drives, steers, brakes and exits after 20 seconds; the final 10 seconds' actual frame intervals go to Evidence/Runtime.json. This sparse scene and a concurrent editor cannot establish final racing performance.

Visual mesh assets/materials live under `/Game/RoadToF1`; temporary pawn and game mode contain no environment generation or race logic. Replace pawn movement with a physics adapter later, retaining camera and mesh attachments as separate components. Race state, checkpoints and AI should remain outside the art and movement layers.

See ASSETS.md for acquisition requirements. Third-party texture files remain local and Git-ignored pending permission to commit; a source-only clone requires those three official CC0 maps before rebuilding materials.
