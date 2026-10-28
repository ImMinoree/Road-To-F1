# Tire-force kart dynamics

**Current default: tire-force dynamics restored for the handling-refinement request.** See [HANDLING_REFINEMENT.md](HANDLING_REFINEMENT.md) for current collision/support behavior and new validation. The earlier no-drift fallback is retained behind `-LegacyKartMovement`. The original implementation notes and historical results below describe the preceding physics pass, including its now-replaced sphere collision and road-height constraint.

The optional custom planar vehicle dynamics use the existing `AProofPawn`. `KartTireModel` integrates mass, local longitudinal/lateral velocity and yaw inertia at a fixed **240 Hz**. `UKartTireDynamics` supplies contact friction, traced road support, gravity when unsupported, swept collision and diagnostics. This is a force-driven 2.5D model, not Chaos Vehicles or a full 3D rigid-body kart. No second pawn, module, race start, HUD or map was created.

The previous `ProofPawn` directly rotated from steering and moved only forward. Inspection of the original repository found the same general swept approach in its playable `AKartPawn`; its separate `ARoadToF1Pawn` uses the Chaos vehicle template. Neither supplied a compatible measured kart tire model to reuse. The original repository was read only. The Instagram clip could not be fetched, so no motion-matching claim is made.

The solver calculates front/rear contact slip angles, smooth lateral-force saturation, a shared longitudinal/lateral friction circle, quasi-static acceleration/braking/cornering load transfer and load sensitivity. The locked rear axle is approximated by shared rear traction, inside-wheel unloading and differential-travel scrub torque. Tire relaxation smooths the return of lateral force after a brake release. Steering sets the front contact direction; **yaw comes from axle-force torque, and lateral travel from integrated forces**. No drift button or direct sideways translation is used. Space is an ordinary brake.

Each axle averages its two contact patches. Explicit physical-material friction takes priority; otherwise contact-face material names, surface tags and finally mesh names select asphalt/curb/grass/dirt coefficients. Unassigned surfaces use asphalt as a documented fallback. Collision remains the existing swept sphere with normal-velocity removal and a slide sweep. Unsupported karts fall instead of automatically teleporting to the grid. Frame hitches accept at most 0.25 s per update; discarded time is reported, rather than using a large unstable integration step.

## Starting settings

These are configurable engineering starting values, not measurements from a particular kart. Select the spawned pawn's **TireDynamics** component in PIE to tune them for that session. Defaults live in `KartTireDynamics.h`; `Parameters()` clamps supported ranges.

| Setting | Default |
|---|---:|
| Kart plus driver mass / yaw inertia | 165 kg / 65 kg·m² |
| Wheelbase / CG to front axle / track / CG height | 1.04 / 0.60 / 1.06 / 0.28 m |
| Front / rear cornering stiffness | 15,000 / 21,000 N/rad |
| Rear grip multiplier / sliding grip drop | 1.10 / 12% |
| Tire relaxation length / axle scrub | 0.18 m / 8 N·m·s |
| Engine force / brake force / rear brake bias | 710 N / 550 N / 100% rear |
| Effective linear drivetrain drag / rolling resistance | 0.32 s⁻¹ / 15 N |
| Steering angle / rate / speed reduction | 24° / 3.2 rad/s / 0.45 |
| Asphalt / curb / grass / dirt friction | 1.05 / 0.85 / 0.48 / 0.42 |
| Drift enter / exit sideslip | 6° / 3° |
| Minimum drift speed / sustain / recovery hold | 3 m/s / 0.12 s / 0.18 s |

The effective drag retains the approximate existing pace; it is not a measured aerodynamic model. Reverse is reduced to a 3.5 m/s range. Negative throttle brakes forward travel, then reverses near standstill. Space brakes without requesting reverse. Steering range reduces with speed. The four existing AIs convert route curvature to the same tire-model steering range and use measured slip feedback; they receive no alternate grip or yaw model.

## Diagnostics and feedback

`GetTelemetry()` exposes longitudinal/lateral speed, sideslip, yaw rate, axle slip angles, axle forces, friction-circle utilization, surface grip, contact count, steering angle and rear inside-wheel loading. The drift latch also requires rear contact slip, meaningful lateral speed, minimum road speed and sustained near-limit rear tire force. A low-speed geometric body angle or wheel angle alone does not trigger it. Rear longitudinal demand is a force/capacity estimate, **not a measured wheel slip ratio**.

Use `-KartTelemetry` or enable `bLogTelemetry` to write 20 Hz CSVs in `Evidence/TireDynamics/drive_*.csv`. Camera vibration includes measured lateral acceleration and rear slip, within the existing tiny angular limits. Cockpit and AI steering poses follow the simulated steering rack. Existing soil/grass debris rates use real slip/traction demand; dust remains restricted to loose surfaces. The optional `TireScrubSound` hook needs an existing looping tire-scrub asset. None was present. There is no asphalt tire-smoke or skid-mark asset, and the combined chassis mesh lacks independently steerable/spinning front-wheel geometry. Those presentations are not claimed complete.

## Repeatable tests

Run `Automation RunTests RoadToF1` in the editor (or launch with `-ExecCmds="Automation RunTests RoadToF1" -TestExit="Automation Test Queue Empty" -ReportExportPath=<output>`). `TireDynamics.ForceScenarios` runs the production solver with fixed inputs and saves eight CSVs plus `engine_scenarios.csv`:

1. Full straight acceleration followed by braking to rest; no yaw or reverse propulsion.
2. Low-speed tight turn; no false drift from the normal body angle.
3. Roughly 40 km/h gentle turn with grip maintained.
4. Excessive steering demand, showing saturation and loss of the requested corner radius.
5. Brake-entry turn from 11 m/s, steering 0.12 and a 0.6 s rear-brake application.
6. The same entry, then brake release and countersteering; verify a small sustained slide and recovery at driving speed.
7. Asphalt-to-loose-surface friction and recovery.
8. Steering while stationary, plus reset/start hold in the world integration test.

`GroundCollisionAndReset` uses a transient physics world to check four contact patches, tagged asphalt/curb/grass/dirt grip, swept wall collision, restart clearing and gravity without road support. Fixed-step results are also compared across 30/60/120 Hz frame groupings. Existing cockpit, AI and debris regressions run alongside these checks.

`Tools/validate_tire_dynamics_pie.py` runs rendered PIE with `-KartDynamicsTest -KartTelemetry`: it checks the original five-kart grid and held-throttle gate, then explicitly stages the player on a temporary off-circuit test pad. It accelerates normally, performs the brake-entry/recovery maneuver, checks dirt/grass debris and restarts the existing race. The pad is unsaved; there are no repositioning calls during a maneuver. `-KartDynamicsTest` is an explicit development-only input latch so zero-axis callbacks cannot overwrite scripted controls. It is inactive in normal Play and shipping builds.

For a manual trial, open `/Game/RoadToF1/Maps/DesertKarting_Visual`, Play and wait for lights-out. W accelerates, S brakes/reverses, A/D steer, Space brakes and R resets. Start with low-speed turns. At about 35–40 km/h, feather A/D for a modest steering input and briefly apply Space; release the brake and ease/countersteer as the rear moves out. Holding full steering at speed or continuing rear braking can spin the kart. The repeatable scripted test uses fractional steering; subjective keyboard handling still needs the player's feedback.

## Reversibility and limits

`Checkpoints/BeforeTireDynamics_20261024` contains the pre-change source/config/tools ZIP, map copies and protected hashes. `-LegacyKartMovement` or `bUseTireDynamics=false` selects the preserved old movement for comparison without restoring files. The archived cockpit development is preserved, and the current cockpit geometry/animations are not overwritten by this change.

No suspension, chassis flex, roll/pitch dynamics, wheel angular-speed solver, tire temperature or kart-to-kart momentum exchange is modeled. The road-height constraint is appropriate to this existing mostly level circuit; it does not establish airborne/uneven-track kart fidelity. Collision uses the prototype sphere rather than a full chassis hull. Packaged builds, force feedback and subjective human handling have not been validated.

## Completed validation

The final Development Editor build passed. All five Unreal automation suites succeeded, including eight force maneuvers and the ground/collision/reset test. The existing SurfaceFX fixture emitted one mobility warning; there were no failed assertions. Native engine maneuver CSVs measured a 9.20° peak countersteer-case sideslip, followed by essentially zero sideslip/yaw at 10.18 m/s. Mild high-speed steering and parked steering did not report a drift. The deliberately excessive corner reached substantial saturation and is not presented as a controlled-slide case.

With the final contact-face sampling code, all four AI racers completed two laps and all 64 sectors in 271.16 simulated race seconds, with zero pre-start motion, measured edge excursions or recoveries. One authoritative start event fired. The diagnostic player also completed more than two laps.

Rendered PIE separately confirmed the original held-throttle gate and launch, followed by a 10.06° peak rear slide and countersteering recovery on the transient pad, dirt/grass grip and debris, and the existing race restart. Maximum pad/road-height error was 0.51 cm and maximum between-frame travel was 226 cm, including screenshot hitches. No repositioning occurred within a maneuver. Five actual cockpit captures were saved; their resolution is the PIE viewport's native size, not a claimed fixed export size. The temporary pad was raised clear of the existing wide desert terrain after an initial fixture overlap was detected. All map hashes and the inspected original-repository source hashes match the checkpoint. `Tools/verify_tire_dynamics.py` checks these reports and decodes the captures; `Evidence/TireDynamics/validation_summary.json` records the result. Attempt logs are retained separately from the final successful reports.
