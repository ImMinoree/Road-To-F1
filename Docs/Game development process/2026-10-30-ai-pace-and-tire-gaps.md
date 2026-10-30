# Game development process - AI pace and tire-wall gap repairs

I improved AI straight-line pace and repaired gaps in the existing tire walls around `/Game/RoadToF1/Maps/DesertKarting_Visual`. Codex assisted with implementation, Unreal validation, screenshots and documentation.

I retained a separate curvature/braking speed envelope so an AI on a clear, settled straight can request its full available pace without unnecessary exit-ramp or personality lifting. Traffic, steering curvature, surface grip, braking and recovery limits remain active. The motor, player handling and tire-force simulation were preserved. The 70 km/h AI setting is a governor, not a guarantee that the unchanged motor reaches it.

I reused the existing red/black tire meshes, materials and two HISM groups. Actual road/curb boundaries and ground support determined placement. The map now has **11,004 tire instances**, 291 more than the previous 10,713, arranged in eight continuous sections. Service crossings and two individual fixture/terrain exclusions remain. I did not rebuild the circuit or change the lighting.

Historical validation for that pass included a save/reload, 2,264 lane/grid clearance sweeps with no new hits, eight barrier collision checks and matched before/after Unreal screenshots. Its ten-kart race completed nine AI first laps without recorded contacts or polygon-corridor excursions; measured peak was about 65.4 km/h and the pace improvement was modest. Those measurements apply to that earlier ten-kart test, not the later 20-kart configuration.

The [full evidence report](../../Evidence/FullPaceAndTireGaps/Report.md), [clearance verification](../../Evidence/FullPaceAndTireGaps/verification.json) and [before/after views](../../Evidence/FullPaceAndTireGaps/BeforeAfter.html) retain the detailed results and limitations. The separate [20-kart report](2026-10-30-twenty-kart-launch.md) records the current grid and later race validation, including its remaining edge excursion and speed limitations.

Changed implementation includes `KartAITrackPlan.h/.cpp`, `TrackRacingAI.cpp`, the existing map, and placement/validation scripts under `Tools/`. Reversible map/source checkpoints remain under `Evidence/FullPaceAndTireGaps/Checkpoint/`.
