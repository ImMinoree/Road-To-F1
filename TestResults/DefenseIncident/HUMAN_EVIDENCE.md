# Human evidence review (evaluation only)

Reviewed 44 sampled frames: 3, 10, 20 and 30 seconds from each of the 11 supplied clips. This is not continuous viewing, frame-perfect synchronization, or a measured NPC speed distribution. Local extracted contact sheets and extraction metadata are retained under `D:/Boring/RaceValidation/DefenseIncidentVideo/`. No footage or telemetry was used to train or install a profile.

- Folder `1`: sampled positions in clip `1t` at 30s show P11; `2t` at 3/10/20/30s shows P6/P5/P2/P1. The last frame has lap time approximately 81.593s. This supports the reported first-lap escape; the exact reported 86-second timing is not independently established by these sparse samples.
- Folder `New folder`: clip `2` at 3s shows P20 and lap time about 56.085s; at 10s it shows P11 and 63.089s. At 20s it shows P5, 73.095s, zero speed, and burning karts. These samples support substantial position gains around a congested incident, not nine individually proven clean passes. Later samples show P2 and then P1.
- Later clear-air samples show the player frequently near 35.4 mph. The attached F9 CSVs measure the player's speed, not every rival's speed. Their original schema does not contain official race position or defense outcomes.

`HumanEvidence.json` contains pre-finish interval summaries for the two likely matching F9 sessions. Matching uses capture end times/durations, not exact frame alignment:

| Likely clip set | F9 session | Player mean mph, first 100s | Samples with kart ahead within 10m, first 100s | Player mean mph, 100-200s | Player contact counter |
|---|---|---:|---:|---:|---:|
| 1 | F8BB65714CD1CC894A084BAAB41AAD0C | 24.09 | 80.54% | 32.64 | 3 |
| New folder | 9D36E2D84AF8D8D4C1FEC0BECD91050C | 22.25 | 84.66% | 30.66 | 3 |

Both sampled sessions have three player contacts. This does not count AI-to-AI incidents visible elsewhere in the field, and does not invalidate the separate earlier human session with higher contacts. No matching human battle sidecars were available, so exact failed-defense and incident-gain attribution is unavailable for these recordings.

## Confirmed code-level causes

1. Previous defense required closing speed above 80 cm/s (2.88 km/h). The 57 versus 55 km/h cap difference alone is only 55.56 cm/s, so it could not trigger that condition. It also selected an arbitrary outer side on straights rather than covering the attacking corridor.
2. Defensive eligibility could use the proposed bypass corridor's free speed while the actual corridor was obstructed. Defense then competed with incident escape planning.
3. A burning kart anywhere ahead could impose the incident limit even in a different physical lane.
4. Rejecting an unsafe intermediate lane also discarded a still-safe final bypass. Rear destination reservations could veto the forward kart's outward escape.
5. The original queue exclusion prevented a genuinely trapped kart from requesting reverse even after the rear corridor cleared. New recovery retains rear occupancy checks, predicted closing checks, static sweeps and bounded duration.
6. Pass commitment could expire while a kart was safely alongside and still gaining longitudinally. The extension is now conditional and limited to three extra seconds.

These causes are established from code and controlled fixtures. They do not prove how much each contributed to an individual pass in the supplied human videos.
