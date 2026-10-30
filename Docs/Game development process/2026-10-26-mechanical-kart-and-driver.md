# Game development process - I integrated a mechanical kart and seated driver

**Date:** October 26, 2026

**Developer:** Me, the human project owner

**Assistance:** Codex assisted with modeling scripts, Unreal integration, testing, and this report.

## What I added

I integrated a versioned kart visual assembly into the existing playable ProofPawn. I added separated steering pivots, front wheel rolling pivots, articulated tie rods, a shared rear axle and drivetrain visuals, pedals, and synchronized seated-driver poses. I kept the existing vehicle simulation authoritative: the visual system reads movement and steering state rather than advancing another simulation.

I connected the steering wheel and driver grip to the actual steering mechanism, with different inside/outside road-wheel angles produced by the visual linkage. Both rear wheels share the axle rotation. I preserved the earlier assets and retained a legacy visual option for rollback.

## How I checked it

The recorded Unreal checks exercised centered and full-lock steering, rapid steering, acceleration, reverse, simultaneous wheel steering and rolling, braking, cornering, drift recovery, collision/restart, and countdown gating. A separate automation sweep checked the fixed-rod mechanism over 481 steering values. The [validation report](../../Evidence/PlayerVehicle_v4/RESULTS.md), [runtime results](../../Evidence/PlayerVehicle_v4/validation.json), and [captured sequence](../../Evidence/PlayerVehicle_v4/steering_sequence.html) describe the actual scope.

## Files and remaining limitations

My editable assembly is [PlayerVehicle_v4.blend](../../Art/PlayerVehicle_v4/PlayerVehicle_v4.blend). The [asset documentation](../../Art/PlayerVehicle_v4/README.md) records the source, hierarchy, Unreal paths, rebuild process and rollback.

The available tire model did not expose wheel angular speed, so rolling uses a documented ground-speed approximation rather than true spinning-wheel slip. The reused driver still needs garment, cuff and contact refinement. Functional tests do not certify photorealism, every mesh intersection, or full-race performance. Later glove changes are documented separately.
