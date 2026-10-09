# Audio and race HUD validation

Implemented: original procedural kart engines; spatial NPC sound; five temporary synthetic commentary cues with captions/cooldown/ducking; twenty round suit-colour/white-centre/black-number badges; mph displays; left-tower lap and centreline distance to lap line in feet; per-racer lap column. Physical speed caps and telemetry units retained.

Validation:
- UE5.8.3 editor and standalone Win64 Development targets built successfully for the audio/HUD implementation.
- All 11 Unreal suites passed (Automation/index.json), including existing full 19-NPC, three-lap, incidents, ordered gate/race/reset and training regressions. Presentation tests verified all 20 engine components and numbers, PCM pitch/silence/clipping, distance semantics, voice assets and absence of km/h HUD text.
- Six PIE suites reported a virtual audio device warning: AUDCLNT_E_RAW_MODE_UNSUPPORTED (Steam Streaming Microphone output). Engine initialized its mixer and tests completed successfully. One connectivity probe warning also occurred. These are recorded in the report, not suppressed. Actual speaker balance and subjective engine realism need the user's listening test.
- Commentary import succeeded with 0 errors/warnings. Narration uses temporary Windows SAPI speech, not the user's recorded voice. The engine sound is an approximation, not a sampled 125cc racing engine.
- Initial render inspected. User supplied a billiard-ball reference during work; revised number labels into original round badges matching suit colours. Final badge editor and standalone builds succeeded. Both presentation suites passed again after the reference-driven change (BadgeAutomation/index.json). Standalone BadgeGame.png inspected and shows coloured round badges with white centres and black numbers.

Limits: route-distance guidance does not validate checkpoint completion. Visual video findings from the preceding phase remain unfixed. No cooked/Steam release validation performed. Raw videos/telemetry/logs remain local. Voice replacements can be recorded using Art/Audio/Commentary/lines.json.
- Standalone HUD image inspected: all20 identities, lap column, player lap/distance and mph are present. Capture is the first game frame and includes Unreal's transient shader-warmup text; BadgeGame.png provides a clearer badge view.
