# Game development process - Twenty-kart grid and full-throttle AI launch

I expanded normal DesertKarting races to **19 AI opponents plus me**, keeping my existing tenth grid position. I extended the existing livery palette to 20 distinct kart colors, preserving the first ten colors and reusing the existing paint/fabric materials. Codex assisted with implementation, testing and documentation.

I removed the AI's extra lights-out reaction hold. For the first 1.25 seconds, opponents retain their staged lateral lanes and use a stopping-distance traffic limit instead of immediately demanding a cruising following gap. They demand full throttle below their safe launch or high-speed target, while braking, collision avoidance, recovery and the existing 70 km/h AI governor remain active.

## Actual validation

- The final normal C++ build and native `TwentyKartDefaultsAndPlayer38Mph` test passed. Live Coding compiled but crashed while applying its patch; the normal module was rebuilt afterward.
- A 150-second real-time PIE race used 19 AI and the existing optional reference player driver, followed by an eight-second race restart test. This was automated driving, not a human replay.
- All 20 grid slots and 20 unique livery colors were verified. No kart moved before lights-out. Both starts produced one authoritative lights-out event and 19/19 full-throttle, zero-brake commands at the first sampled control update (about 0.12 seconds).
- All 19 AI completed a lap in **91.72–114.57 seconds**. No swept contacts were recorded. One low-speed corridor excursion occurred while yielding at segment 496; clean racing in every situation is not proven.
- AI controller cost averaged **0.421 ms**, maximum **1.155 ms**. This excludes rendering and physics. No dropped simulation time was reported.

## Speed limitation

The AI ceiling is 70 km/h, but the measured peak was **65.44 km/h**. Only **0.286%** of aggregate AI racing time was at 65–70 km/h; full throttle occupied 43.47%. I have **not achieved 65–70 for most of a lap**. Corners/traffic require braking, and the unchanged motor/drag model has an estimated flat straight equilibrium near 67.2 km/h. I did not add hidden power, grip or position boosts to disguise this limitation.

The map, player pawn and tire-dynamics source hashes remained unchanged during validation. Existing uncommitted work was preserved. This implementation pass did not commit or push; source control is handled separately on my explicit request.

## Files and evidence

I changed `TrackRacingAI.h/.cpp`, `KartRaceSettings.h`, `KartMechanicalVisuals.cpp`, and updated the existing default/racecraft tests. Repeatable validation and summarization are in `Tools/kart20_validate_live.py` and `Tools/kart20_summarize.py`.

See [measured results](../../Evidence/TwentyKartLaunch/summary.json), [raw validation](../../Evidence/TwentyKartLaunch/validation.json), [telemetry](../../Evidence/TwentyKartLaunch/telemetry.csv), [driver-camera screenshot](../../Evidence/TwentyKartLaunch/grid_first_person.png), [final build log](../../Evidence/TwentyKartLaunch/build_final.log), and [reversible checkpoint](../../Evidence/TwentyKartLaunch/Checkpoint/). The initial 20-kart launch trial remains in `Evidence/TwentyKartLaunch/InitialLaunch/`.

To play, open `Road_To_F1_New.uproject`, load `/Game/RoadToF1/Maps/DesertKarting_Visual`, and press **Play**. Normal Play automatically spawns 19 opponents; wait for the existing five lights to go out. The reference autopilot is enabled only by explicit test command-line flags.
