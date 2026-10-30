Tilted heading-up circuit minimap
Play DesertKarting_Visual. The lower-left full-circuit map rotates with player yaw.
Red player dot and white opponent dots are preserved. M opens the existing flat full map.
The shallow perspective compresses the distant edge; a small shadow adds depth.
MinimapTilt is editable on KartNavigationMap (default 0.72, range 0.5..1).
Heading uses shortest-angle exponential smoothing at 25/s, avoiding wrap jumps at +/-180.
Scale is rotation-invariant so the circuit does not zoom/pump while turning.
Joined triangle strips with transparent one-pixel fringes replace aliased line primitives.
Dots use 32-sided discs with a feathered edge. No noisy material, particles or world capture.
Fixed arrays avoid per-segment allocation overhead; strokes are batched per layer.

build_final.log: final C++ build.
result.json and unreal_verified.log: final actual PIE validation.
Screenshots demonstrate initial and 90-degree rotated headings; all ten karts tracked.
The scripted heading check temporarily disables pawn actor ticking before setting yaw,
only in the unsaved PIE world, so tire dynamics does not restore its own yaw state.
Other karts are repositioned in PIE to make the dots visible around the whole circuit.
Initial checks tried to set actor yaw before the authoritative grid released it; their failed
assertions are retained in attempt1.json and attempt2.json. No physics or circuit code was modified.
Checkpoint contains original navigation source files for reversal. No commit or push.

