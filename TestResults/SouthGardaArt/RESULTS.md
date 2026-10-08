# South Garda / kart art pass — 2026-10-08

Implemented: local Three.js HTML viewer, five selectable kart component groups, livery colour, exploded view, OrbitControls, turntable and camera reset. Tubular frame, four tires, body fairings, bucket seat, steering, pedals, radiator, engine fins, exhaust, axle, chain and disc brake geometry. Separate venue scene with approximate 1,236 m route, 9 m asphalt, kerbs, paddock, pit building, seating canopy, team tents, service vehicles, trees and distant hills.

Unreal: imported 20 material mesh batches, authored materials and CC0 asphalt texture. Saved `/Game/RoadToF1/SouthGarda_ArtPreview` and `/Game/RoadToF1/Art/SouthGardaV01`. Preserved RacePrototype and the two pre-existing modified VehicleBasic external actors.

Verified: browser rendered both scenes; component isolation, exploded view, colour change, orbit drag, wheel zoom and reset worked. Browser warning/error log was empty. Unreal import commandlet completed successfully (one engine deprecation warning); saved map reloaded, 20 mesh actors and metre-to-centimetre dimensions verified, all material slots inspected and assigned. Corrected Unreal OBJ handedness for placements and explicit named Rotator fields. Rendered and visually inspected UnrealVenueFinal.png. Fixed browser track triangle winding and camera near plane to eliminate track-surface artifacts.

Screenshots: BrowserKart.png, BrowserVenue.png, UnrealVenueFinal.png. Machine report: import-report.json and verified-bounds.json; final verification run: verify-materials.log.

Not tested/implemented in this map: driving laps, kart rig, handling, AI, ordered gates, lap HUD and finish detection. Static art is a first blockout; trees, hills and buildings are placeholders, not production realism. Approximate route is not a surveyed South Garda replica. No C++ changes or new compilation required for this art pass. No paid purchases, subscription system, commit or push performed.

Next: refine the authentic track layout using authoritative references, replace scenery placeholders with appropriately licensed realistic meshes, improve kart surfacing and rig it, then connect race gates/HUD and test complete laps on the new venue.
