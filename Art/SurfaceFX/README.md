# Rear-tire surface effects

Original soil-chip, grass-clipping and soft dust assets. No downloaded textures or plugins. Blender source: `SurfaceFX.blend`; authoring and import scripts: `Tools/surface_fx_author.py`, `Tools/surface_fx_import.py`.

Runtime component `UKartSurfaceFX` is attached to every `AProofPawn`, including existing AI pawns. It reads actual actor displacement and traces below each rear tire after pawn movement. Rear contacts are editable and start at X=-55 cm, Y=±53.5 cm, Z=-31 cm relative to the current pawn, based on the existing kart model's rear axle. It never supplies input, applies forces, changes grip or modifies AI/race logic.

Grass throws short-lived clippings, soil chips and a restrained dust trail. Soil/sand/gravel throw chips and dust. Asphalt, curbs, runoff and concrete suppress emission; unknown surfaces fail quiet. Classification uses the hit mesh/material names and actor/component tags, so custom surfaces can use `SurfaceGrass`, `SurfaceDirt` or `SurfaceAsphalt`. Actual physics surface types can replace this adapter when the production tire solver is integrated.

Emission requires horizontal motion over 120 cm/s and ground contact within 18 cm of the tire footprint. The effect stops at rest, airborne, disabled, beyond 65 m from the local camera, or on a teleport/reset step. Existing particles fade out. Reverse movement throws debris opposite the measured travel direction. Acceleration and yaw rate modestly increase emission; these are visual approximations, not measured tire slip or wheelspin.

Rendering uses three reusable native instanced-mesh pools per kart, 32 slots each (96 total), with no particle collision, dynamic shadows, ray-tracing visibility or replication. No per-particle actors are created. Dust billboards face the local camera and use a soft procedural opacity shader with per-instance fading. Dedicated servers skip the component. Assets have an Always Cook label; packaged and multiplayer rendering still need validation.

To tune or disable: select the pawn's `RearTireSurfaceFX` component (or Blueprint subclass) and edit `bEnabled`, `MinimumSpeedCm`, `EffectDistanceCm`, `RearLeft` and `RearRight`. Materials live in `/Game/RoadToF1/SurfaceFX/Materials`. Removing the component's constructor attachment restores the prior cosmetic behavior without changing the driving code.

Build the Editor target and open either DesertKarting map. Press Play, wait for lights-out, then drive onto the infield. The trail is behind the rear tires; an external view is more useful than the forward cockpit for inspecting it. Stop or return to asphalt and emission ceases.

Tests: `RoadToF1.SurfaceFX.ContactAndPooling` checks two-wheel and split-surface contact, stopped expiration, asphalt suppression, reverse, airborne, disabled behavior, fixed pool size, no particle collision/replication and unchanged owner transforms. `Tools/validate_surface_fx_pie.py` performs transient diagnostic motion and captures actual PIE views; it never saves either map. The diagnostic tests effects, not driving handling. Evidence is under `Evidence/SurfaceFX`.
