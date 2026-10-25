# Road_To_F1_New - Integrated desert kart

The current playable map is DesertKarting_Visual, with the original circuit, start grid and authoritative five-red-light sequence, plus the V5 kart chassis and existing animated first-person arms/wheel on ProofPawn. See [INTEGRATION.md](INTEGRATION.md) for assets, validation evidence and known prototype limitations. The earlier VisualProof milestone notes below remain historical context.

Four track-edge AI opponents are described in [RACING_AI.md](RACING_AI.md). The local cockpit now has gentle speed-based FOV widening, restrained vibration and depth-masked peripheral blur; settings and validation are described in [SPEED_EFFECTS.md](SPEED_EFFECTS.md).

The default pawn now uses substepped tire-force dynamics with real lateral velocity, rear-brake oversteer and countersteering recovery. See [TIRE_DYNAMICS.md](TIRE_DYNAMICS.md) for settings, diagnostics, repeatable tests and the reversible checkpoint. Space is a normal brake; W/S, A/D and R keep their existing roles. `-LegacyKartMovement` selects the previous movement for comparison.

Open `Road_To_F1_New.uproject` in installed Unreal 5.8.3, open `/Game/RoadToF1/Maps/DesertKarting_Visual`, press Play, click viewport. W accelerates, S brakes/reverses, A/D steer, Space brakes, R resets, Escape exits PIE. Driving unlocks when the five red lights go out. `Tools/PlayIntegrated.ps1` launches the same map as a standalone preview. The default planar tire-force model retains swept sphere collision and traced ground support. Its starting power/drag settings approach roughly 47.4 km/h on a straight; the preserved legacy mode retains the original 57.6 km/h hard cap.

`Tools/Open.ps1 -Profile Balanced` launches the game at 1920×1080, High scalability (2), 75% internal resolution, conventional shadows. `-Profile Validation` selects Epic (3), VSM and 100% internal resolution. TSR and software Lumen are configured; hardware ray tracing is disabled. No Nanite forced onto the small road meshes. Manual daylight exposure is held constant. No motion blur, bloom, grain or artificial sharpening added.

Reproduce geometry with `D:\Boring\blender.exe -b -t 4 --python Tools/model_proof.py`. The `.blend` uses metres; FBX exports are individually imported in centimetres, with longitudinal UV repeat every 2 m. Rebuild level using UnrealEditor-Cmd with `-run=pythonscript -script=<absolute Tools/build_scene.py> -nullrhi -unattended`. This intentionally replaces only this project's VisualProof map. Rendering validation must use a real RHI, never NullRHI.

Capture using UnrealEditor.exe with `-ExecCmds="py <absolute Tools/capture_scene.py>" -unattended -nosplash`. Three fixed 1920×1080 views are saved under Evidence after settling. The capture script exits its own editor. Do not invoke against another editor with unsaved work.

Runtime bounded test: UnrealEditor.exe `<absolute uproject>` `/Game/RoadToF1/Maps/VisualProof` `-game -windowed -ResX=1920 -ResY=1080 -ProofSmokeTest -unattended`. This automatically drives, steers, brakes and exits after 20 seconds; the final 10 seconds' actual frame intervals go to Evidence/Runtime.json. This sparse scene and a concurrent editor cannot establish final racing performance.

Visual mesh assets/materials live under `/Game/RoadToF1`; temporary pawn and game mode contain no environment generation or race logic. Replace pawn movement with a physics adapter later, retaining camera and mesh attachments as separate components. Race state, checkpoints and AI should remain outside the art and movement layers.

See ASSETS.md for acquisition requirements. Third-party texture files remain local and must not be committed without permission; a source-only clone requires those three official CC0 maps before rebuilding materials.
