# RoadToF1 build log

## 2026-10-07 — Phase 1: verified baseline and editing route
- Branch: `milestone-1-race-loop`, tracking `origin/milestone-1-race-loop` at `00d4d94`.
- Installed Unreal: 5.8.3, changelist 58210709.
- No AGENTS.md files found in the repository or applicable parent directories.
- Existing untracked Blueprints, RoadToF1 map, external actors, and external objects are preserved.
- Vehicle template C++ module and time-trial variant exist. No new race-loop implementation yet.
- Computer Use enumerates Unreal but both fresh capture attempts failed (`FrameArrived timed out` / `window capture timed out`). No UI edits performed.
- Direct project filesystem access works. Investigating read-only commandlet asset inspection and native build/test route.
- Prior log remains at `C:\Users\GBURG-4\Documents\Codex\2026-10-07\referenced-chatgpt-conversation-this-is-an\outputs\BUILD_LOG.md`; this repository log continues it.

## Phase 2: saved-asset inspection and implementation
- Read-only Unreal Python commandlet successfully loaded the saved RacePrototype map; 0 errors in the successful inspection.
- Saved BP_StartFinish: `(4489.925, 601.219, 20)`, StartFinishTrigger extent `(100,1200,250)`, facing approximately -Y. PlayerStart at `(4450,0,102)`, facing +Y. `CompletedLaps` is absent in the saved asset.
- Landscape spline meshes confirm a circular 4500 cm radius circuit. Configured CP1 `(0,4500,100)` facing -X, CP2 `(-4500,0,100)` facing -Y, CP3 `(0,-4500,100)` facing +X.
- Added deterministic race state, forward swept gate detection, map-scoped runtime integration, native UMG HUD, timers, finish state, F5/button restart, and visible gate markers. No Content asset writes.
- Inspection initially encountered Zen startup failure; successful commandlets use `InstalledNoZenLocalFallback`. A spline-property inspection attempt failed, then was corrected to use the supported spline-mesh API.
- Initial sandboxed build hit an access denial while backing up UBT's default log. Retried with approved build access and a workspace log.
- First isolated editor build succeeded in 142.30 seconds. Build/test copy: `D:\Boring\RaceValidation\RaceLoop-20261007` (copied Content, not linked to originals).
- Final build adds PIE integration tests and fixes explicit HUD height plus teleport detection. Tests are pending; no gameplay success claimed yet.
- Existing open editor still has the old DLL loaded. No editor shutdown, hot reload, commit, or push performed.

## Phase 3: automated validation passed
- Final isolated editor build: **Succeeded**, 100.96 seconds.
- Unreal automation report: **3 succeeded, 0 failed, 0 warnings/errors in the tests**.
- `RoadToF1.RaceLoop.GateGeometry`: passed swept forward/high-speed/rotated gates and reverse/lateral/vertical/repeated-sample rejection.
- `RoadToF1.RaceLoop.Rules`: passed ordered checkpoints, skipped/repeated/reverse rejection, three-lap completion, lap records, frozen timers, reset and second race.
- `RoadToF1.RaceLoop.PrototypePIE`: passed in the saved RacePrototype map copy. Verified existing trigger discovery, HUD creation, scripted vehicle-position crossings, finish, frozen total time, and restart to PlayerStart.
- These are automated/scripted integration tests. Manual driving and HUD visual appearance have not been validated.
- Machine-readable result: `TestResults/RaceLoop-20261007.json`. Full logs/report remain in `D:\Boring\RaceValidation\RaceLoop-20261007`.
- Google Drive plugin created and readback-verified a native build-log document in the ChatGPT folder: https://docs.google.com/document/d/1G50AjsZ8HPWBww885N6fpBy7-2dn4fBq4sYXDAxsy_k/edit
- Independent rendered screenshot instance launched; shaders compiling. Screenshot still pending.
- Asked user to save unsaved assets and close the original Unreal editor before rebuilding the actual project's DLL. Capture failure prevents checking unsaved state safely. Original project source/config is updated; original loaded binary remains unchanged.

## Phase 4: rendered HUD inspection
- Standalone game from the isolated copy successfully rendered the prototype at 1280 × 720 using the existing PC shader cache.
- Captured and visually inspected `TestResults/RaceHUD.png`: waiting-state lap/checkpoint labels, lap/total/last-lap timers, instructions and restart button are visible without clipping. The template speed/gear HUD remains visible.
- Transient engine texture-loading messages were hidden only in the screenshot instance using DisableAllScreenMessages; the original Blueprint print behavior and project settings are untouched.
- Rendering used the existing sports car placeholder. This phase does not claim kart artwork/handling or manual driving validation.
- Closed the separate screenshot instances after capture. Kept the original editor running.
- Original BP_StartFinish and RacePrototype hashes match the pre-test copied assets. `git diff --check` passes. Requested branch remains active.
- **Pending:** user saves/closes original Unreal, then actual-project build and reopening to load the new classes. Source/config changes, docs and tests remain uncommitted on milestone-1-race-loop.

## Phase 5: actual project built and tested
- User closed Unreal; process check confirmed neither UnrealEditor nor UnrealEditor-Cmd was running before the build.
- Built the actual `RoadToF1.uproject` on `milestone-1-race-loop`: **Succeeded**, 70.41 seconds. Native module DLL updated successfully.
- Ran the complete race-loop automation suite against the actual saved project: **3 succeeded, 0 failed, 0 test warnings/errors**, process exit 0.
- Actual-project report: `TestResults/RaceLoop-ActualProject-20261007.json`; full logs/report in `RoadToF1/Saved/Logs/RaceLoopBuild.log`, `RaceLoopActualTests.log`, and `RoadToF1/Saved/RaceLoopActualReport`.
- Requested reopening the actual editor directly on `/Game/RoadToF1/RacePrototype` to load the new module. Manual driving validation remains the next step.
- Reopen verified: UnrealEditor process 18740 is responsive; startup log confirms engine initialization and loading the actual RacePrototype map. Start/finish Blueprint and map asset hashes are unchanged across the actual-project tests. Google Doc log updated and readback-verified.
- No commits, pushes, or Content asset edits performed. Existing untracked work remains preserved.

## Phase 6: version-control handoff
- User requested committing and pushing the completed work to GitHub.
- Included race-loop source/config, the existing prototype Blueprint/map with all World Partition external actors/objects, documentation, inspection tool, test reports, and HUD screenshot.
- Validation carried forward: actual-project build succeeded; all three automation suites passed with zero test warnings/errors; `git diff --check` passes.
- Target: `origin/milestone-1-race-loop`. Git history records the commit and remote synchronization.

## 2026-10-08 — Startup-map correction
- User reported the lap/timer HUD missing after reopening. Runtime log confirms PIE started `VehicleBasic`, rather than `RacePrototype`.
- Cause: EditorStartupMap and GameDefaultMap still pointed to the original Vehicle template map. The race subsystem intentionally activates only in RacePrototype.
- Changed both defaults in DefaultEngine.ini to `/Game/RoadToF1/RacePrototype.RacePrototype`. No C++ rebuild required.
- Verified RacePrototype exists and no Saved/Config map defaults override the settings.
- Preserved two existing user modifications in VehicleBasic external-actor assets.
- Current editor session still needs to open RacePrototype; defaults apply on subsequent launches. This config-only correction uses the previously built/tested race implementation.

## 2026-10-08 — South Garda and kart art pass
- User selected South Garda Karting, Italy. Created Art/KartLab/index.html and local Three.js viewer with all requested kart parts, orbit/zoom, component isolation, exploded view, paint and turntable controls.
- Downloaded Three.js 0.180.0 (MIT) and Poly Haven Asphalt Track diffuse (CC0). Author/source and licenses recorded in Art/KartLab/README.md. All meshes authored locally; no purchases.
- Imported 20 material mesh batches into a new /Game/RoadToF1/Art/SouthGardaV01 folder and saved /Game/RoadToF1/SouthGarda_ArtPreview. Existing RacePrototype and user-modified VehicleBasic external actors preserved.
- Verified browser interactions and empty warning/error log. Unreal import succeeded; saved map reloaded and scale/material actors verified. Corrected camera rotation and imported handedness. Visually inspected final Unreal render. Evidence and detailed results in TestResults/SouthGardaArt/RESULTS.md.
- Initial art blockout only: approximate route; scenery placeholders still need realistic replacements. Kart is static art, not a rigged driving pawn. Race gates/HUD have not been integrated or driving-tested on the new map. Existing RacePrototype remains the tested race-loop map.
- No C++ changes, commit or push in this phase. Next: accurate layout/scenery refinement, kart rig, race-loop integration and full driving validation.

## 2026-10-08 — playable Unreal kart and South Garda integration
- Added native KartPawn/KartGameMode and ordered RaceTrackGate actors. Created separate SouthGarda_KartRace map with kart spawn, follow camera, 12 checkpoints and start/finish. Connected HUD, speed, lap/total timers, three-lap finish and F5 reset.
- Controls: W accelerate, S brake/reverse, A/D steer, Space brake, F5 restart. First arcade movement implementation; no Chaos kart rig, animated driver/wheels, AI or penalties yet.
- User saved and closed Unreal before the C++ build. UBA stalled; -NoUBA standard compiler build succeeded. First automation found invalid keyboard-axis binding; fixed press/release bindings and rebuilt successfully.
- Final automation: all four suites passed, zero errors/warnings, including original prototype regression. New map tests actual movement, braking/ground support, 600 road collision samples, ordered gate rules, three-lap finish/frozen timing and reset. Programmatic gate sweeps are not a full human-driven lap test.
- Rendered and visually inspected TestResults/SouthGardaGameplay/KartRace.png. Detailed evidence: TestResults/SouthGardaGameplay/RESULTS.md and AutomationFinal/index.json.
- Updated project startup/default map to SouthGarda_KartRace. Preserved RacePrototype, SouthGarda_ArtPreview and user-modified VehicleBasic external actors. No commit/push performed.
- Next: user handling feedback, kart/wheel/driver animation, authentic layout and realistic scenery refinement, then AI/flags/penalties.

## 2026-10-08 — user-reported track and handling fixes
- Replaced raised collision-enabled grid/finish meshes with flush non-colliding surface paint and proper two-lane positioning boxes. Finish paint now aligns with the actual race gate.
- Replaced spaced kerb boxes with continuous curve-following strips and white edge paint. Removed sparse placeholder barriers and floating debug gate outlines in the kart driving view; checkpoint hints are surface lines.
- Reduced forward cap 90 -> 55 km/h and acceleration 6.5 -> 3 m/s². Added gradual A/D steering, smooth recentring and filtered/capped yaw. Reset clears steering/yaw state.
- User saved/closed Unreal for the build. Backed up affected maps/meshes in D:/Boring/RaceValidation/KartControlFixes-Before. Preserved map actors/transforms and unrelated user work.
- Build succeeded; surface patch completed. All four automation suites passed, zero errors/warnings. Extended regression verifies long straight traversal past markings, speed limit and steering ramp, alongside road collision/lap/finish/reset tests. Visual evidence and results: TestResults/KartControlFixes/.
- Saved locally, not committed/pushed. Next: user driving feedback before more handling tuning.

## 2026-10-08 — black corner patches and grass-edge trapping
- Found reversed/folded road and kerb triangles at tight original curve bends. Smoothed uniformly sampled route; all 16,840 road/kerb/paint triangles now have positive upward area. Updated existing checkpoint/spawn alignment.
- Replaced centre-only ground support with footprint probes and a bounded 12cm climb, retaining swept collision. Kart can cross grass/asphalt transitions in forward and reverse.
- User saved/closed Unreal. Backups in D:/Boring/RaceValidation/CornerRejoinFix-Before; unrelated user changes retained.
- Build and asset import succeeded. All four Unreal automation suites passed, zero errors; one unrelated HTTP connectivity timeout warning. All 48 driven rejoin regression cases passed.
- Evidence and limitations: TestResults/CornerRejoinFix/RESULTS.md. Separate review-camera map used for corner rendering; playable map preserved. Next: user driving validation at the reported bends.
- No commit or push performed.

## 2026-10-08 — South Garda/kart GitHub handoff
- User requested pushing the completed map, kart and fixes before driver-model work, then AI/NPCs.
- Package includes native kart/gates/HUD integration, startup map, authored Three.js/OBJ assets, imported Unreal assets/maps, tools, test evidence and latest corner/rejoin fixes.
- Validation: native build succeeded; four Unreal automation suites passed, zero errors (one unrelated network timeout warning); 48 driven grass-to-road recovery cases and 16,840 triangle geometry checks passed.
- Existing changes to two old VehicleBasic external actors remain local and preserved, outside this implementation commit.
- Target branch: origin/milestone-1-race-loop. Next phase: seated helmeted driver model using the supplied image as visual reference, followed by AI opponents.

## 2026-10-08 — seated drivers and 19 AI opponents
- Added original F1-inspired seated driver art: suit/panels, gloves, boots, full-face helmet and curved visor. Six imported mesh batches and runtime livery parameters; 20 distinct suit colours verified. Driver assets included in cooking. Static seated prototype, without a skeletal animation rig.
- Expanded the open-ended starting boxes to 20 slots on the straight. Player starts P20; native KartRaceDirector spawns 19 opponents. Player cap 57 km/h, AI cap 55 km/h; AI slow in corners, avoid traffic and reverse to recover from blocked movement.
- Opponents wait for player acceleration. Position HUD and retained finish order added; F5 resets the complete field. Ordered gate rules/timers retained.
- Full-race test first found route switching at nearby track sections and bunching. Restricted AI tracking to contiguous route samples, retained lane choices, added swept recovery and static-world ground probes so karts cannot serve as ground for each other.
- Final build succeeded (59.25s); final asset import succeeded. All five automation suites passed with zero errors/warnings. All 19 AI physically drove three ordered laps within 600 simulated seconds; speed limits, 20 unique colours, six loaded meshes per racer, field/grid reset and previous handling/rejoin/rules regressions passed.
- Visually inspected GridFinal.png and DriverFinal.png. Evidence: TestResults/DriverAI/RESULTS.md and AutomationFinal/index.json. Human player's kart is parked off-track during autonomous race verification; human competitive race remains the next driving check.
- User saved/closed Unreal before edits. Backups in D:/Boring/RaceValidation/DriverAI-Before. Original RacePrototype and user-modified VehicleBasic actors preserved. Reopening SouthGarda_KartRace for user testing.
- This phase is saved locally; no commit or push performed.

## 2026-10-08 — driver and AI GitHub handoff
- User requested pushing the seated-driver and 19-opponent phase.
- Include driver source/Unreal assets, native AI director, 20-slot grid, 57/55 km/h limits, position HUD/reset, import/review tools and final successful test report/screenshots.
- Final validation: all five automation suites passed with zero errors/warnings; all 19 AI completed three ordered laps; all 20 suit colours distinct and six driver meshes loaded per racer.
- Keep unrelated VehicleBasic external-actor edits and raw engine logs local. Target: origin/milestone-1-race-loop.

## 2026-10-08 — remaining local changes handoff
- User reported changes remaining after the driver/AI push. Verified all source commits were already synchronized with GitHub.
- Remaining tracked changes are two pre-existing VehicleBasic external-actor assets; include their current saved versions to preserve the user's map edits in GitHub.
- Added ignore rules for raw engine logs and intermediate driver/AI build reports/screenshots. These files remain on disk; final test report and final screenshots remain tracked.
- No gameplay source changes. Existing five-suite validation applies to the driver/AI implementation; these older map asset edits were not separately gameplay-tested.

## 2026-10-09 — racecraft, collisions, leaderboard and engine compatibility
- User requested less repetitive NPC driving, collision/fire response, incident avoidance and a named/numbered speed leaderboard; push and merge only after user testing and approval.
- Repository was on main at dea3d96 after an external merge. Created local ai-racecraft-incidents; preserved all saved assets. Backed up original project/source to D:/Boring/RaceValidation/Racecraft-Before.
- Engine-created RoadToF1 5.8 copy matched original Source/Config/Content by SHA-256 before edits. Both use the installed UE 5.8.3, CL58210709. Corrected original EngineAssociation from a custom GUID to 5.8. The copy remains local and ignored; its editor is still open, so consolidation awaits saved/closed confirmation and a fresh comparison.
- Implemented 19 individual driving profiles, traffic-scored gradual lane changes with commitment periods on straights, swept collision slowdown/stun, hard-impact six-second mesh flame/smoke/lighting, contact cooldown/reset, and slowing/holding/choosing open lanes around burning incidents. Kept player57/NPC55 km/h limits.
- Added live 20-row leaderboard with unique fictional names, kart numbers, positions, speeds and player/incident highlighting. Retained lap/checkpoint/timing/finish/reset UI on the right.
- Initial full-field regressions exposed traffic deadlock: a rear kart blocked forward escape. Fixed occupied-lane rejection to apply to lane changes, not current-lane forward travel. Reduced corner profiles to the controller's tested range. Visual checks exposed viewport anchors being reset by SetPositionInViewport; fixed call order and incident text/panel sizing.
- Native build succeeded. All six automation suites passed, zero errors/warnings. All 19 AI physically completed three ordered laps in 600 simulated movement seconds. Actual swept collision, hard/light impact, cooldown/reset, and a follower avoiding a two-kart burning blockage passed. Rendered incident validation also passed; screenshots inspected.
- Evidence and prototype limitations: TestResults/Racecraft/RESULTS.md. Fire uses lightweight animated meshes; competitive difficulty and collision feel still need human driving feedback. Raw logs and intermediate failed reports retained locally.
- Changes saved locally; no commit, push or merge. Next: save/close copied editor, preserve any new unique copy edits, retire duplicate safely, open original for user driving test, then request push/merge approval.

## 2026-10-09 — single-project consolidation
- User confirmed the copied project was saved and closed. Verified no Unreal processes remained before moving files.
- Fresh SHA-256 comparison found identical Content; copy Source matched the pre-change backup and copy Config matched HEAD. No unique saved user changes needed transfer.
- Moved the entire duplicate with native Move-Item to D:/Boring/RaceValidation/RetiredProjects/RoadToF1-5.8-20261009 after checking exact source and destination paths. No files deleted. Repository now has only the original RoadToF1 project folder; retired copy is a recovery backup outside Git.
- Original project uses UE5.8.3 and already has the successful native build, six-suite regression and rendered incident validation. No gameplay changes during consolidation.
- Reopened original SouthGarda_KartRace with the UE5.8.3 executable; verified the process command line targets the original project and the editor is responsive (RoadToF1 - Unreal Editor). Launch log retained at TestResults/Racecraft/user-review-launch.log.
- Next: user driving test. Push and merge remain pending explicit approval.

## 2026-10-09 — racecraft publication authorization
- User explicitly requested pushing and merging all work completed so far, then creating a subagent and a separate AI Agent for game training directory.
- Publishing the completed and consolidated racecraft phase with its six passing regression suites and rendered incident evidence. Live manual driving by the assistant remains unverified because Computer Use capture timed out.
- Training-agent files are excluded from this publication and developed as a separate phase.

## 2026-10-09 — telemetry-first training agent
- Completed racecraft publication: main and ai-racecraft-incidents both verified at 03cb890 on GitHub. A lock during branch switching was resolved by hashing the two material assets against the published blobs and retaining their identical versions; no user assets changed.
- User authorized a subagent, exact directory AI Agent for game training, recorded gameplay as primary input, modular learning/video/style/evaluation and publication after workflow/test checks. Created ai-game-training from main. User saved/closed Unreal for compilation.
- Subagent delivered independent Python modules, whole-session holdout, contextual aggregate fitting, reproducible distinct 19-driver styles, strict validation and optional video/manual-observation intake. Main agent added native F9 recorder, session rotation on F5, aggregate candidate learner, validated startup profile loading and recording/style HUD.
- Native modules compile in runtime targets so they can accompany a packaged PC game. Optional reviewed profiles staged from Content/Training. Recording off by default; no automatic uploads/collection. Future signup consent is required before any automatic collection. Python/Codex subagent remain development tools.
- UE5.8.3 editor build and standalone Win64 Development game build succeeded. All nine Unreal suites passed, zero errors/warnings; existing full 19-NPC race regression retained. Native candidate/default-off/capture/reset/schema tests passed. Eleven Python tests passed after resolving sandbox fixture permissions.
- Three actual native test CSVs validated end-to-end offline (47 samples; 2 train sessions/1 holdout). Nondeployable automation provenance retained; not represented as human learning. No real player/video data supplied, no performance improvement claimed. Evidence/limits: TestResults/Training/RESULTS.md and AI Agent for game training/RESULTS.md.
- Publish only framework/code/test evidence; raw recordings, candidates, logs and retired project backup remain local. Next: player drives using F9, then evaluate candidate race performance before approving any learned styles. Cooked/Steam release and signup UI remain later work.
