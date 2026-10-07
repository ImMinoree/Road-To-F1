# Milestone 1 race loop

## Playing
- Open `/Game/RoadToF1/RacePrototype` and press Play after building and reopening Unreal.
- Drive forward across the existing `BP_StartFinish` line to start lap 1.
- Follow the circular track counterclockwise: CP1 at the top, CP2 on the left, CP3 at the bottom, then start/finish on the right.
- Complete three laps. The HUD freezes total time and the final lap time at the finish.
- Press **F5** to clear all race progress/times and return the vehicle to PlayerStart. The restart button also works when the mouse is available in PIE (Shift+F1).
- The next gate is green. Other gates are blue; finished gates are grey.

## Implementation and configuration
- `URaceLoopSubsystem` activates only in game/PIE worlds named `RacePrototype`.
- It reads the existing Blueprint's `StartFinishTrigger` geometry at runtime. It does not modify the Blueprint, its graph, variables, or saved map assets. Its existing print event remains.
- `DefaultGame.ini` configures the lap target and checkpoint locations/yaws. They match the saved circular landscape spline: radius 4500 cm, starting at the right side and driving towards +Y.
- Checkpoints use swept forward plane crossings within the gate width and height, rather than component overlap events. Repeated, out-of-order, reverse, and outside-gate crossings cannot advance progress. High-speed crossings are detected between frames.
- Movements larger than the prototype's plausible per-frame travel limit reseed detection, preventing large teleports from sweeping through gates. This is a prototype safeguard, not competitive anti-cheat.
- Race/lap clocks use world game time, so world pauses stop the clock. Crossing times are interpolated within the sampled frame.
- Pawn replacement resets the race. F5 resets race state and vehicle physics. Standard template vehicle recovery controls remain available.
- `URaceLoopWidget` constructs the HUD in C++; no new binary UI assets are required.
- This phase does not add kart handling, AI rivals, penalties, or career progression.

## Validation
Automation tests are under `RoadToF1.RaceLoop`:
- `Rules`: start, three laps, skipped/repeated/reverse crossings, recorded lap times, frozen finish time, reset and second race.
- `GateGeometry`: forward/reverse, rotated gates, high-speed crossing, lateral and vertical misses, repeated samples.
- `PrototypePIE`: opens the saved prototype in a separate editor instance; checks existing trigger discovery, HUD creation, scripted vehicle-position crossings, finish and restart. This is scripted integration coverage, not a manual driving/handling test.

With the project editor closed, build `RoadToF1Editor Win64 Development` using Unreal 5.8.3. Run tests with `UnrealEditor-Cmd.exe <uproject> -NullRHI -unattended -nosound -ddc=InstalledNoZenLocalFallback -ExecCmds="Automation RunTests RoadToF1.RaceLoop" -TestExit="Automation Test Queue Empty" -ReportExportPath=<report-directory>`.

See `BUILD_LOG.md` for actual results and remaining validation limitations.
