# Dynamic racing HUD — validation

Implemented in the existing native C++ UMG widget on branch `dynamic-racing-hud`, using the existing race subsystem and director data.

- Seven racers around the player, with a teal player highlight; holding Tab shows all 20.
- Initial standings hold 5 seconds, periodic standings every 20 seconds hold 3 seconds, position changes extend visibility. Fade in takes 0.25 seconds and fade out 1 second. A single game-clock state controller avoids stacked animations/timers.
- Start briefing holds 6 seconds and fades over 1 second. Resetting or starting the race reinitializes its schedule.
- Permanent corner panels display position, lap, MPH and current lap time. Captions and recording status remain supported.
- Existing native UMG implementation uses render-opacity animation rather than introducing Blueprint animation assets or extra modules. Widgets are allocated once; standings refresh at 20 Hz.
- Removed the engine's F5 shader-complexity debug binding so F5 serves the existing race restart action.

## Files
- `RaceLoopWidget.cpp/.h`: layout, data refresh, visibility integration.
- `RaceHUDVisibility.h`: independent visibility schedule and standings window.
- `RaceLoopSubsystem.cpp`: presentation reset on restart/respawn.
- `Config/DefaultInput.ini`: F5 shortcut conflict.
- `Tests/RaceHUDTests.cpp`: timing, input/reset integration and optional development-only screenshot fixture.

## Verification
- UE 5.8.3 Editor Development build succeeded.
- Visibility schedule and input/reset PIE tests passed. Commandlet PIE does not paint Slate, so the test explicitly runs the same data synchronization function used by NativeTick. Tab and F5 use actual PlayerController input events.
- Standalone rendered captures confirm initial compact standings/briefing, hidden side panels with permanent HUD, and full standings while Tab is held.
- Full regression: 13/13 suites passed, zero test errors or warnings (Automation/index.json).
- Final 1280x720 captures inspected after spacing fixes: initial, minimal, full-field and restart states. F5 keeps normal rendering after removing the debug binding. Earlier 1600x900 captures exposed the spacing issues and remain local.
- Build has deprecation warnings for the development fixture using the existing PlayerController input API; compilation succeeds on UE 5.8.3.

## Limits / manual checks
- No human-driven lap or subjective animation review was performed. Position-change and recurring visibility are tested with controlled race-clock inputs; screenshots exercise actual UMG rendering.
- Ultra-wide and unusual UI scaling settings still need manual review. No gameplay/AI/physics changes are part of this phase.
- Optional visual fixture: run standalone with `-ExecCmds="RoadToF1.HUDCapture <absolute-output-directory>"`; captures occur at 2, 8, 10 and 14 game seconds. It is excluded from shipping builds.
