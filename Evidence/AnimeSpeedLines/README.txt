Anime-inspired peripheral speed lines
Open /Game/RoadToF1/Maps/DesertKarting_Visual, Play, and accelerate in first person.
F3 toggles the speed lines and existing cockpit speed FOV/blur/vibration together.
V and C select third-person/look-back cameras, where these lines are absent.

One post-process material on DriverEye:
/Game/RoadToF1/SpeedEffects/M_KartAnimeSpeedLines
Procedural, antialiased angular streaks travel radially outward. No particles or textures.
Depth protects the nearby cockpit; radial and lower-screen masks protect sightline/hands.
At most two additional scene-color taps provide restrained peripheral blur.
It runs before HUD rendering, so map, countdown, mirror and warning arrows stay legible.
The existing modest FOV response is reused; no extra shake or FOV system was added.

UKartSpeedLines is a component on the existing RaceStartHUD.
Editable/Blueprint controls: Enabled, Intensity, StreakCount (8..160), ThicknessPixels
(0.3..3), Opacity (0..0.7), AnimationSpeed (0.1..3), VanishingPoint,
StartKmh (25), NoticeableKmh (45), StrongKmh (65), FullKmh (85), PeripheralBlur.
ActualSpeedKmh reads ProofPawn.GetVelocity().Size2D()*0.036, including tire dynamics.
Thresholds map to strengths 0, 0.15, 0.6 and 1, with smooth interpolation.
Strength uses exponential time smoothing; streak phase advances in game seconds.
The effect is zero at/below 25 km/h, disabled, during staging/restart or other views.
The material defaults to zero strength when not driven, including asset previews.

Validation files: build.log, material_build_final.log, Automation/index.json,
pie_result.json, unreal_verified.log, actual PIE PNGs.
The development test drives with the existing test-input API; no movement code or
physics values are changed. Actual driving screenshots cover stationary, 20, 35, 50 km/h.
The 80 km/h screenshot is explicitly a paused post-process parameter preview, not an
80 km/h driving run: the existing speed cap is 38 mph (~61 km/h).
Initial harness expected 55 km/h before the bend; it was adjusted to the verified
50 km/h section, then parked the other karts in the unsaved test world to remove traffic variability. Initial attempt logs/results are retained, not final validation results.
Toggle testing invokes the bound action through Python, not OS keyboard synthesis.
No comparative GPU benchmark or packaged build was performed.
Source/map SHA-256 checks in the PIE harness verify no on-disk changes during testing.
Checkpoint preserves the pre-change HUD files. No commits or pushes were made.

