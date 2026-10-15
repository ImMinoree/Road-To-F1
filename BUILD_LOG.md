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

## 2026-10-09 — supplied gameplay video review
- User supplied bad start.mp4 (366.03sec) and trial 1.mp4 (310.70sec) from local NVIDIA recordings. Both file timestamps predate the telemetry recorder. No corresponding human CSV sessions found.
- Extracted local 1280px sample frames at two-second intervals and inspected contact sheets/key frames. Source files untouched; videos and frames remain local. Workspace-only FFmpeg utility installed under D:/Boring/VideoReviewTools.
- Parent reviewed bad_start; authorized training subagent reviewed trial_1 independently. Both show launch congestion and NPC incidents; trial_1 reaches first by15sec, before first bend. bad_start shows first by93sec. Later player/NPC contacts and postfinish contact are visible. Exact inputs, impact initiators and continuous lane oscillation cannot be established from sparse frames.
- Saved VIDEO_REVIEW.md and event annotations, separating observed behavior from code-derived hypotheses. Failed launches/incidents are evaluation examples, not approved positive training data. No policy fit/installed, gameplay code altered, build run, commit/push/merge in this review phase.
- Next: controlled regression for forward/reverse launch, initial actual lane vs planned lane, queued waiting vs stuck recovery, avoidance without fire, and safe postfinish behavior. Capture new human sessions using F9 for exact controls and traffic context.

## 2026-10-09 — kart audio, commentary and race presentation
- User requested player/opponent kart sounds, commentary, numbers above drivers, top-left lap/distance details and mph displays. User saved/closed Unreal and requested a clear Git change description. Created kart-audio-race-hud from synchronized main; retained pending video-review documents.
- Implemented original per-kart procedural two-stroke approximation driven by speed/throttle, quieter spatialized NPC engines, burning-engine silence and narration ducking. Added camera-facing overhead racer numbers for all20 racers.
- Added event-based start/lap/overtake/incident/finish commentary, captions, routine cooldown and restart reset. Generated five temporary Windows SAPI narration WAVs locally, imported sound assets and assigned them on the existing SouthGarda_KartRace director. User voice can replace those clips later; no cloning or microphone collection.
- Top-left tower now includes player lap, forward track distance to the lap line in feet, individual racer laps, names/numbers and mph. Physical57/55km/h limits and telemetry schema stay consistent (35.4/34.2mph). Distance display is guidance; ordered checkpoint rules still validate laps.
- First UE5.8.3 editor build succeeded and commentary import completed with0 errors/warnings. Final audio/HUD regression and visual inspection in progress. No fixes to the earlier launch/traffic incidents are claimed in this phase.
- Final validation: all 11 Unreal suites passed with no errors; six PIE suites recorded the virtual WASAPI raw-mode compatibility warning and one connectivity probe warning. Report retains those warnings. Editor and standalone Development targets passed; two presentation suites passed again after changing numbers to reference-inspired round badges. Standalone badge render inspected. Human listening remains needed for actual output balance.
- User supplied a round numbered-ball reference during implementation. Used original sphere geometry, suit-coloured outer shells, white centres and black numbers; no image texture copied. Badge identity and distance/mph HUD tests passed. Documented temporary narration source, voice replacement workflow and unaddressed launch/traffic findings.
- Prepared clear feature/validation/limitations Git description on kart-audio-race-hud. Publish branch for user testing; merge awaits explicit approval of this new gameplay version.

## 2026-10-09 — approved audio/HUD merge
- User explicitly requested merging kart-audio-race-hud. Verified clean starting tree and fetched origin; main was an ancestor of the tested branch at80db677.
- Unreal locked the saved map and five sound assets during branch switching. Verified each file's Git blob hash exactly matched the tested commit, then advanced main/index and synchronized only unlocked files. Saved locked assets remained intact; working tree was clean.
- Fast-forwarded main to the tested audio/HUD/video-review commits. Existing11-suite and final presentation/build validation applies; this merge adds no gameplay changes.

## 2026-10-14 — dynamic racing HUD
- Inspected existing native C++ UMG widget, RaceLoopSubsystem progress and KartRaceDirector standings; reused them on dynamic-racing-hud from main. UE 5.8.3. User saved and closed Unreal for build work.
- Added compact seven-racer window, player accent, full-field Tab override, scheduled/position-triggered fades, start briefing and permanent position/lap/MPH/lap-time corner panels. Widgets are allocated once; standings update at 20 Hz.
- One game-clock opacity controller handles holds, fades and retriggers. F5/respawn resets presentation. Removed the conflicting engine F5 shader-complexity debug shortcut after detecting it in rendered QA.
- Editor build succeeded. All 13 Unreal suites passed with zero test warnings/errors, including existing gameplay regression. Fixed a test helper endpoint and explicitly synchronized UMG in commandlet PIE, which has no painted viewport.
- Actual standalone UMG captures inspected at 1600x900 and final 1280x720; corrected cramped columns/time display. Final captures confirm initial, minimal, full standings and restart states. No manual driving session performed; periodic/position transitions verified with controlled schedule tests.
- Files and evidence: TestResults/DynamicHUD/RESULTS.md. No AI, physics, assets, checkpoint or timing logic changed. Next: user playtest, especially fades during overtakes and preferred readability. Publication/merge held for user review.

## 2026-10-15 — packed race stability (local, awaiting human playtest)
- Verified clean main at 761e6d0bddfe3e6dc3a90e6b2d9e58dbeb9ddc82 and origin ImMinoree/Road-To-F1, read project history/handoff, created fix/packed-race-stability. User saved/closed Unreal. Existing assets preserved; no project copy, push or merge.
- CONFIRMED: absolute-speed release accepted reverse; physical +/-200 cm grid disagreed with planned +/-130 cm lanes; a legitimate frozen queue requested reverse after three seconds with rear traffic present. Baseline controlled tests reproduce all three failures. Code inspection confirmed planned-position lane safety and continued competitive driving after finish. Footage-specific impact initiators remain unproven. Existing official result freezing already worked; preserved rather than replaced.
- IMPLEMENTED: directional intentional launch, measured initial corridors/eight-second launch hold, rotated footprints/actual lateral occupancy/relative-motion prediction, committed lane clearance, generalized slow/stopped obstruction handling, rear-checked bounded stuck recovery and cooldown, contact braking, checkpoint approach guidance, safe finisher coasting with kart collision filtering and full reset. Player57/NPC55 km/h caps, styles, ordered rules, HUD, assets and training architecture retained.
- Parameter rationale: equal initial launch throttle prevents rear acceleration catch-up; local obstruction target400 cm/s and lane-target rate240 cm/s allow clearance before reaching blockers with original steering smoothing. Passing options extend to +/-300 cm, penalized outside normal lanes. Predictive braking uses1200 cm/s² plus0.1-second allowance. Gate guidance preserves each physical corridor rather than forcing a center merge; gate acceptance remains unchanged. Full rationale in TestResults/PackedRace/RESULTS.md.
- Changed KartPawn.h/.cpp, KartRaceDirector.h/.cpp, new Tests/PackedRaceTests.cpp, diagnostics in Tests/KartIntegrationTests.cpp, .gitignore, report/evidence and this log. No map/material/other binary assets modified.
- AUTOMATED TESTED: fresh Final/index.json reports14/14 RoadToF1 suites passing, zero test errors/warnings. All19 NPCs complete three ordered laps within unchanged600 simulated seconds (398.4–596.9s). Eight-second20-kart launch has0 contacts and0.1cm first-second lane drift. Controlled slow/stopped/two-kart non-burning passes have0 subject contacts. Queue/rear/stuck/contact/displacement/finish/reset regressions pass, as do existing incident/HUD/rules/audio/training suites.
- BUILD VERIFIED: final UE5.8.3 Editor Win64 Development succeeded11.44s; standalone Win64 Development succeeded57.03s. git diff --check passed. Baseline expected failures and final JSON retained; intermediate reports/raw logs kept locally and ignored, not deleted.
- MANUALLY VERIFIED: none in this phase; headless PIE exercises real actors/collision, not a human driving or visual-quality assessment. No cooked/Steam claim.
- LIMITATIONS: full-race contacts remain. Racer7 misses CP7 once (513cm lateral vs480cm gate half-width), completes valid ordered progress later, and finishes596.9s with only3.1s margin. Immobilization fixture does not prove every physical obstacle escape. Finishers ignore all kart collisions and may visibly overlap active racers while retaining world collision. Arbitrary blocked bends and competitive feel require human tests.
- NEXT: follow the nine-step PIE checklist in TestResults/PackedRace/RESULTS.md, capture F9 human packed-race sessions, inspect first-corner merges/CP7 displacement/contact rates and completion margin. No synthetic test telemetry approved for learning. Publication held for user instruction.

## 2026-10-15 — measured AI race flow and pace (local)
- Continued fix/packed-race-stability at761e6d0 with all prior uncommitted stability changes preserved. Verified origin ImMinoree/Road-To-F1 and no running user Unreal editor. Backed up prior director/test source outside Git. No project copy, asset change, commit, push or merge.
- DIAGNOSED FIRST: added opt-in limit snapshots and test-owned speed/brake/queue statistics before tuning. Baseline14/15 suites pass; new train assertions fail. Clear-air reaches54.94 km/h; seeded exits reach95% cap in2.85s. Thus the55 km/h cap is not the measured problem. Baseline field moving average19.67mph, traffic94.96s/NPC, guidance53.22s/NPC, obstruction2.90s/NPC. Normal passing did not inherit the emergency400cm/s cap.
- CONFIRMED: short pursuit lookahead with smoothed steering causes large lateral oscillation on straights; gate guidance interrupts planned lanes and applies an edge slowdown inside otherwise valid corridors; rejected intermediate lane targets linger and yield zero target speeds; narrow binary speed control repeatedly brakes/coasts. No stale corner timer found. Corner and traffic constraints already combine by minimum, not multiplicative compounding. Human footage did not provide exact distributions.
- IMPLEMENTED: longer high-speed straight-only lookahead, preserve safe planned gate lanes, retain normal pursuit when aligned, measured-lane planner reset after rejection, tracked pass consideration/commitment/clear states, bounded stronger/proportional exit throttle, brake hysteresis, immediate traffic reductions with800cm/s² release. Original corner limits, physical safety margins,57/55km/h caps, launch/recovery/finish and other systems preserved. No KartPawn physics changes in this phase.
- AUTOMATED TESTED: Final/index.json15/15 pass, zero test warnings/errors. All19 finish by487.5s under unchanged600s limit; mean finish376.54s versus443.82s. Moving average22.72mph (+15.5%); >30mph time31.97% versus17.21%; mean brake events170.32 versus315.95. Summed per-kart contacts42 versus49 (not unique pairs). Launch and controlled blockage avoidance remain zero-contact.
- New fixtures verify clear-air cap, three controlled exits, six-kart train, intentional safe normal pass, no erroneous emergency cap, lane commitment, prompt traffic release and state reset. Train followers stay above40km/h and finish near55km/h with no contact; pass has one tracked completion, no flips/contact; removed-obstacle limit clears within2s. Existing14 suites all pass. Intermediate tuning failures kept locally; no assertions relaxed. Train filter is explicitly seeded when preparing44km/h moving traffic, avoiding artificial inherited grid limits.
- Changed KartRaceDirector.h/.cpp, existing Tests/KartIntegrationTests.cpp, new Tests/PaceMetrics.h and Tests/RacePaceTests.cpp, .gitignore, BUILD_LOG and TestResults/RacePace reports/script/JSON. Raw logs and intermediate exports ignored without deletion.
- Editor Win64 Development build succeeded (final incremental6.04s); standalone Win64 Development succeeded (507.19s, cold PCH load). Initial compiler wait was resolved by retrying only the task-owned build and reading the large PCH into cache. Existing HUD InputKey deprecation warnings remain; no new compiler errors. git diff --check passed.
- MANUAL TESTING: not performed by assistant. Headless PIE exercises actual actors and swept collisions. No package/cook/Steam claim. Exit tests use controlled25.38km/h seeds near three bend exits, not natural-apex measurements. Full-race contacts and a slower487.5s finisher remain; one deterministic track/profile setup is not proof against all human traffic.
- NEXT: human full-race F9 capture using the six-step checklist in TestResults/RacePace/RESULTS.md; inspect passing, brake waves, CP7, corner exits and slowest racer. Per-NPC and field comparisons in METRICS.md. Do not raise AI cap or publish without further instruction.


## 2026-10-15 � bounded human-versus-AI battle behavior (local playtest candidate)
- Verified fix/packed-race-stability, HEAD761e6d0bddfe3e6dc3a90e6b2d9e58dbeb9ddc82, origin ImMinoree/Road-To-F1, and no running user editor before edits. Preserved earlier uncommitted pace/stability work. No project copy, assets changed, commit, push, or merge. User explicitly resolved caps to player57/NPC55 km/h.
- CONFIRMED: no prior defensive state or recent player-loss memory; no explicit side-overlap corridor hold; pass intent could be missed when a lane was chosen before the consideration timer elapsed. No per-reason pass cancellation counters. Finishers remained visibly parked indefinitely. Existing human CSVs support early traffic/clear-air contrast and contact variance, but not exact P20-to-P1 timing because they lack positions. Human evidence evaluated only, not trained/installed.
- BASELINE: fresh instrumented Baseline/index.json15/15 pass, moving22.72mph, meanfinish376.54s,last487.50s,contacts42,passes63attempts/3completions. Baseline and final evidence separate.
- IMPLEMENTED: one-side bounded defense with lateral-move time/closing-gap feasibility, 2�3s hold/six-second cooldown, physical side-overlap corridor hold, six-second same-lap local player-repass window, promotion of already-selected safe pass intent, reason counters, optional development-only five-Hz F9 battle sidecar and offline evaluation summary. Existing safety and57/55caps unchanged. Original F9 schema/learner untouched.
- FINISH: retain frozen results and coast; hide NPC presentation only after at least4s and below1km/h. No teleport or immediate destruction. Existing finisher collision filtering retained, so brief coasting overlap remains a manual visual limitation. Reset restores visibility/battle state. Active racing collision unchanged.
- AUTOMATED TESTED: final16/16 suites pass with zero test warnings/errors; both RoadToF1Editor Win64 Development(20.00s) and RoadToF1 Win64 Development(243.64s) build successfully. git diff --check passes. Existing HUD InputKey compiler deprecation warnings remain. No package/cook/Steam validation claim.
- New BattleTests exercise bounded defense, fixed-side hold, actual closing-attacker movement without contact, no alongside block, separate moving corridors, safe committed overlap, no erroneous400cm/s cap, completed player repass, distant-player exclusion, corner-entry corridor choice, finish retirement and reset. F9 optional sidecar flush/original-header compatibility passes; parser verified19rows/47fields. Existing launch/train/blockage/reverse/ordered race/HUD/audio/training suites preserved.
- FINAL FIELD: all19 finish; moving22.87mph,>30mph32.85%,meanfinish367.56s,last378.90s,contacts28 (summed per-kart, not unique incidents).45defense events;52passattempts/3completions. Abort reasons26occupied/16timeout/7contact-risk; no direct corner/guidance/speed-loss cancellations. Full-field player parked, hence zero player-repass events; controlled fixture one loss/one attempt/one completion/zero contacts. Alongside fixture minimum41.02km/h for3s with zero contacts. Launch remains zero-contact; all19 finishers retire visible parked presentation by test end.
- First behavior iteration regressed to53contacts and386.46s mean finish; refined closing-gap feasibility and safe intended-lane hold instead of retaining that iteration. Intermediate reports kept locally. Final pass accounting correction makes attempts more faithful but absolute full-field completions still3; do not claim passing frequency solved.
- Changed this phase: KartRaceDirector.cpp/.h, new KartBattleState.h, KartPawn.cpp visibility reset, new Tests/BattleTests.cpp, Tests/KartIntegrationTests.cpp metrics/assertion, .gitignore, this log, and TestResults/Battles evidence/reports/evaluation scripts. Other existing modifications belong to previous phases and remain intact.
- MANUAL TESTING REQUIRED: no human driving/visual verification performed by assistant. Do not claim P20-to-P1 resistance solved. Follow nine-step PIE checklist in TestResults/Battles/RESULTS.md with -RaceBattleDebug and F9; evaluate defense fairness, sustained corner overlap, actual positions gained, repass opportunities, coasting overlap, and restart. Per-NPC metrics in METRICS.md. Stop for human playtesting; publication remains unauthorized.


## 2026-10-15 - defense effectiveness and incident containment (local human-playtest candidate)
- Verified branch fix/packed-race-stability, HEAD 761e6d0bddfe3e6dc3a90e6b2d9e58dbeb9ddc82, original project, UE 5.8.3 (Build.version), and no user editor running before edits. Preserved earlier uncommitted work/assets; no commit, push, merge, project copy or cap change. Player/NPC remain 57/55 km/h.
- HUMAN EVIDENCE: reviewed 44 sampled frames across all 11 supplied clips, not continuous video. Read two likely matching F9 sessions as evaluation only; no training/profile installation. Frames support first-lap clean-air escape and major gains around a congested incident. Original CSV lacks positions/defense details; exact pass causes and reported 86/166-second milestones cannot be independently established. HUMAN_EVIDENCE.md and HumanEvidence.json preserve observations and limits.
- CONFIRMED ROOT CAUSES: defense closing threshold 80 cm/s exceeds the cap-speed advantage (55.56 cm/s); arbitrary straight defense lane; eligibility checked intended rather than actual corridor; burning kart slowdown ignored lateral conflict; unsafe intermediate targets discarded safe final escape lanes; rear reservations could veto forward escape; queue rules prevented bounded recovery from a stationary dead end; pass timeout ignored safe ongoing progress.
- IMPLEMENTED: feasible 25 cm/s/eight-second closing-horizon defense with one 3-6-second lane hold and six-second cooldown, actual-corridor clearance and incident/rejoin exclusion. Physical-corridor incident handling, earlier slow-object detection, temporary bypass preferences, preserved safe final plans, scoped rear-corridor escape and stable parallel-motion prediction. Conditional pass extension capped at three seconds. Stationary dead-end recovery waits 1.5 seconds, reverses at most two seconds with existing static sweeps and extended rear-motion prediction; normal queue/reverse rules retained. No global handling/collision changes.
- DIAGNOSTICS: opt-in development RoadToF1.BattleDebug 1 or -RaceBattleDebug emits separate five-Hz battle-v2 CSV alongside F9. Original 19-column training schema untouched. Defense outcomes, incident/rejoin state and field containment metrics added. Evaluation-only analyzer emits heuristic gain categories and UNKNOWN when no matched crossing; prevents reuse and stale-defense attribution. Four analyzer tests pass; real generated sidecar has consistent 74 columns.
- BASELINE/FINAL: fresh separate exports; baseline 16/16 suites, final 17/17 suites, zero automation warnings/errors. Editor Win64 Development passed (15.83s); standalone game Win64 Development passed (263.47s). git diff --check passed with line-ending notices only. No packaging/cook/Steam or rendered human-playtest claim.
- FINAL FIELD: all 19 finish ordered three laps. Mean moving speed 22.87 -> 22.62 mph; above30mph 32.85 -> 31.62%; mean finish 367.56 -> 368.16s; last 378.90 -> 382.10s. Summed per-kart contacts 28 -> 23 (not unique pairs). Launch stays zero-contact. Passes 52 attempts/3 completed -> 72/11; occupied aborts 26 -> 29, timeouts16 ->31, contact-risk7 ->0. Defense activations45 ->142; final outcomes14 held,22 late,24 alongside,25 occupied,1 threat-clear,56 lost-speed. Held is a controller window outcome, not proof against an adaptive human.
- INCIDENT FIXTURES: nine followers clear both-sided obstruction in19.20s; eight clear one-sided obstruction in27.35s, zero contacts in both. Every follower reaches90% cap within10s of clearance; last one-sided follower2.80s. Full field548 per-NPC low-speed episodes,12 secondary contact-counter increments,longest multi-kart queue4.10s,mean completed episode0.77s,mean completed recovery5.78s. These detailed baseline counters were unavailable; episodes are not unique crashes.
- REJECTED ITERATIONS: broader defense caused45 contacts; global far-corridor rejection forced traffic into one lane; an early short reverse left one follower delayed. Kept intermediate evidence locally and did not relax existing safety assertions. Final incident fixture observes36s for recovery but requires clearance under30s. Existing launch/train/blockage/reverse/checkpoint/finish/reset/HUD/audio/training checks all pass.
- CHANGED THIS PHASE: KartRaceDirector.cpp, KartBattleState.h, Tests/BattleTests.cpp, new Tests/IncidentTests.cpp, Tests/KartIntegrationTests.cpp, .gitignore, this log and TestResults/DefenseIncident reports/scripts/JSON. Director header and pawn edits visible in Git status belong to earlier work and were preserved.
- MANUAL TESTING REQUIRED: no new human driving/visual verification performed. First-lap P20-to-P1 resistance remains unproven; defense often releases for safety, pass timeouts remain common, one incident follower still takes27.35s to clear, and moving pace is slightly lower. Delayed finisher hiding/reset tests pass, but visual coasting overlap needs observation. Follow the ten-step PIE/F9/video checklist in TestResults/DefenseIncident/RESULTS.md. Stop for human playtest; no publication authorized.

## 2026-10-15 - publication approved
- User explicitly authorized commit, push and merge of the completed packed-race stability, pace, battle and incident-containment work.
- Verified validated source SHA-256 hashes match, final 17/17 automation result and both successful Windows Development builds; git diff --check passed. Fetched origin/main remains 761e6d0, allowing a conflict-free fast-forward of the tested tree.
- Earlier no-publication statements and VALIDATION.json describe the pre-approval test snapshot. Human competitiveness and visual playtest limitations remain applicable after publication.
