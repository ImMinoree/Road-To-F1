# Battle regression metrics

Contacts are summed per-kart counters, not unique incidents. Moving speed means >1 mph. Automated fixtures are not a human competitive benchmark.

## Baseline

Suites: 16 passed / 0 failed.

Mean finish 367.56s; last 378.90s; contacts 28.
Mean moving speed 22.87 mph; mean time above 30 mph 32.85%.
Pass attempts 52; completions 3; ratio 0.058.
Defenses 45; repass attempts/completions 0/0. Player is parked during full-field test, so player repass counts should be zero.

| NPC | Finish s | Avg mph | Peak mph | >30 % | Traffic s | Brakes | Contacts | Pass attempts/completions | Defense | Alongside s | Loss | Repass attempts/completions |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 372.6 | 22.85 | 34.18 | 32.2 | 59.6 | 155.0 | 3 | 1/0 | 2 | 109.15 | 0 | 0/0 |
| 2 | 342.3 | 24.21 | 34.18 | 38.3 | 5.2 | 157.0 | 0 | 0/0 | 2 | 23.3 | 0 | 0/0 |
| 3 | 349.5 | 23.76 | 34.18 | 34.5 | 35.1 | 158.0 | 1 | 3/0 | 1 | 56.65 | 0 | 0/0 |
| 4 | 358.7 | 23.44 | 34.18 | 34.7 | 46.2 | 160.0 | 3 | 1/0 | 3 | 55.45 | 0 | 0/0 |
| 5 | 345.1 | 23.89 | 34.18 | 35.3 | 37.3 | 161.0 | 0 | 1/0 | 3 | 56.05 | 0 | 0/0 |
| 6 | 371.6 | 22.9 | 34.18 | 33.6 | 98.6 | 166.0 | 2 | 4/0 | 3 | 119.0 | 0 | 0/0 |
| 7 | 372.0 | 22.67 | 34.18 | 32.3 | 109.0 | 192.0 | 2 | 4/1 | 3 | 106.6 | 0 | 0/0 |
| 8 | 357.7 | 23.16 | 34.18 | 34.3 | 55.8 | 160.0 | 0 | 0/0 | 4 | 110.55 | 0 | 0/0 |
| 9 | 373.3 | 22.75 | 34.18 | 33.3 | 76.6 | 155.0 | 1 | 3/0 | 3 | 96.7 | 0 | 0/0 |
| 10 | 373.6 | 22.51 | 34.18 | 32.2 | 89.8 | 185.0 | 1 | 3/0 | 0 | 85.4 | 0 | 0/0 |
| 11 | 375.7 | 22.21 | 34.18 | 32.0 | 73.1 | 154.0 | 3 | 0/0 | 3 | 76.4 | 0 | 0/0 |
| 12 | 370.5 | 22.96 | 34.18 | 31.9 | 105.2 | 153.0 | 4 | 1/0 | 2 | 83.0 | 0 | 0/0 |
| 13 | 377.3 | 22.39 | 34.18 | 32.0 | 77.6 | 161.0 | 2 | 3/0 | 3 | 82.0 | 0 | 0/0 |
| 14 | 374.1 | 22.35 | 34.18 | 30.6 | 87.6 | 167.0 | 0 | 6/1 | 0 | 84.55 | 0 | 0/0 |
| 15 | 378.0 | 22.54 | 34.18 | 30.5 | 85.6 | 180.0 | 3 | 3/0 | 2 | 99.7 | 0 | 0/0 |
| 16 | 378.9 | 22.02 | 34.18 | 31.1 | 87.0 | 164.0 | 1 | 6/1 | 1 | 71.75 | 0 | 0/0 |
| 17 | 360.6 | 23.42 | 34.18 | 33.3 | 63.9 | 153.0 | 1 | 3/0 | 3 | 103.25 | 0 | 0/0 |
| 18 | 376.1 | 22.19 | 34.18 | 30.8 | 99.1 | 153.0 | 1 | 7/0 | 1 | 66.25 | 0 | 0/0 |
| 19 | 376.1 | 22.39 | 34.18 | 31.3 | 95.1 | 163.0 | 0 | 3/0 | 6 | 121.05 | 0 | 0/0 |

Detailed defense/incident diagnostics were not present in this baseline; unavailable, not zero.

Abort totals: occupied=26, corner=0, guidance=0, speed_loss=0, timeout=16, contact_risk=7, rival_unavailable=0.
Corner/guidance/speed-loss outcomes remain zero when there is no explicit cancellation for that reason; speed limits are recorded separately.

### Captured scenarios and outcomes

```
BATTLE racer1 defenses=2 alongside_s=109.15 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=1 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer2 defenses=2 alongside_s=23.30 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=0 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer3 defenses=1 alongside_s=56.65 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=3 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer4 defenses=3 alongside_s=55.45 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=0 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=1 rival_unavailable=0 hidden=1
BATTLE racer5 defenses=3 alongside_s=56.05 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=1 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer6 defenses=3 alongside_s=119.00 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=1 corner=0 guidance=0 speed_loss=0 timeout=3 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer7 defenses=3 alongside_s=106.60 losses=0 repass_attempts=0 repass_completed=0 completed=1 occupied=2 corner=0 guidance=0 speed_loss=0 timeout=1 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer8 defenses=4 alongside_s=110.55 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=0 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer9 defenses=3 alongside_s=96.70 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=0 corner=0 guidance=0 speed_loss=0 timeout=2 contact_risk=1 rival_unavailable=0 hidden=1
BATTLE racer10 defenses=0 alongside_s=85.40 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=1 corner=0 guidance=0 speed_loss=0 timeout=2 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer11 defenses=3 alongside_s=76.40 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=0 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer12 defenses=2 alongside_s=83.00 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=1 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer13 defenses=3 alongside_s=82.00 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=2 corner=0 guidance=0 speed_loss=0 timeout=1 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer14 defenses=0 alongside_s=84.55 losses=0 repass_attempts=0 repass_completed=0 completed=1 occupied=3 corner=0 guidance=0 speed_loss=0 timeout=1 contact_risk=1 rival_unavailable=0 hidden=1
BATTLE racer15 defenses=2 alongside_s=99.70 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=3 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer16 defenses=1 alongside_s=71.75 losses=0 repass_attempts=0 repass_completed=0 completed=1 occupied=3 corner=0 guidance=0 speed_loss=0 timeout=1 contact_risk=1 rival_unavailable=0 hidden=1
BATTLE racer17 defenses=3 alongside_s=103.25 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=2 corner=0 guidance=0 speed_loss=0 timeout=1 contact_risk=0 rival_unavailable=0 hidden=1
BATTLE racer18 defenses=1 alongside_s=66.25 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=1 corner=0 guidance=0 speed_loss=0 timeout=3 contact_risk=3 rival_unavailable=0 hidden=1
BATTLE racer19 defenses=6 alongside_s=121.05 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=2 corner=0 guidance=0 speed_loss=0 timeout=1 contact_risk=0 rival_unavailable=0 hidden=1
SIDE min_kmh=41.02 contacts=0 alongside_s=3.00 defenses=0
REPASS losses=1 attempts=1 completed=1 contacts=0
CLEAR speed_kmh=54.85 t90=4.75 d90_cm=3288 t95=5.00 d95_cm=3643
EXIT120 apex_kmh=25.38 one=35.86 two=46.33 three=54.32 t90=2.35 d90_cm=2427 t95=2.60 d95_cm=2781 contacts=0
EXIT210 apex_kmh=25.38 one=35.86 two=46.33 three=54.32 t90=2.35 d90_cm=2446 t95=2.60 d95_cm=2799 contacts=0
EXIT300 apex_kmh=25.38 one=35.86 two=46.33 three=51.51 t90=2.35 d90_cm=2456 t95=2.60 d95_cm=2812 contacts=0
TRAIN0 min_kmh=38.88 final_kmh=54.68 contacts=0 ahead_cm=-1.0 closing_cms=0.0 peak_mph=34.18 moving_avg_mph=29.61 under20_pct=0.0 under25_pct=28.5 over30_pct=50.0 traffic_s=0.0 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=1 brake_s=0.1 longest_queue_s=0.0
TRAIN1 min_kmh=40.26 final_kmh=54.72 contacts=0 ahead_cm=-1.0 closing_cms=0.0 peak_mph=34.18 moving_avg_mph=31.53 under20_pct=0.0 under25_pct=0.0 over30_pct=69.0 traffic_s=2.8 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=1 brake_s=0.1 longest_queue_s=0.0
TRAIN2 min_kmh=40.57 final_kmh=54.85 contacts=0 ahead_cm=506.4 closing_cms=4.3 peak_mph=34.18 moving_avg_mph=31.51 under20_pct=0.0 under25_pct=0.0 over30_pct=66.0 traffic_s=3.7 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=0 brake_s=0.0 longest_queue_s=0.0
TRAIN3 min_kmh=41.07 final_kmh=54.72 contacts=0 ahead_cm=-1.0 closing_cms=0.0 peak_mph=34.18 moving_avg_mph=31.60 under20_pct=0.0 under25_pct=0.0 over30_pct=64.5 traffic_s=3.3 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=0 brake_s=0.0 longest_queue_s=0.0
TRAIN4 min_kmh=41.69 final_kmh=54.85 contacts=0 ahead_cm=488.9 closing_cms=4.1 peak_mph=34.18 moving_avg_mph=31.62 under20_pct=0.0 under25_pct=0.0 over30_pct=67.5 traffic_s=4.3 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=0 brake_s=0.0 longest_queue_s=0.0
TRAIN5 min_kmh=42.39 final_kmh=54.98 contacts=0 ahead_cm=1584.1 closing_cms=-1.6 peak_mph=34.18 moving_avg_mph=31.66 under20_pct=0.0 under25_pct=0.0 over30_pct=69.5 traffic_s=4.6 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=0 brake_s=0.0 longest_queue_s=0.0
PASS success=1 flips=0 contacts=0 emergency=0 final_kmh=54.77 attempts=1 completed=1
RELEASE blocked_cms=188.3 clear_cms=1527.8 after_s=2
20-kart 8s launch: contacts 0, first-second lane drift 0.1 cm
```

## Final

Suites: 17 passed / 0 failed.

Mean finish 368.16s; last 382.10s; contacts 23.
Mean moving speed 22.62 mph; mean time above 30 mph 31.62%.
Pass attempts 72; completions 11; ratio 0.153.
Defenses 142; repass attempts/completions 0/0. Player is parked during full-field test, so player repass counts should be zero.

| NPC | Finish s | Avg mph | Peak mph | >30 % | Traffic s | Brakes | Contacts | Pass attempts/completions | Defense | Alongside s | Loss | Repass attempts/completions |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 374.7 | 22.13 | 34.18 | 29.6 | 61.0 | 176.0 | 0 | 7/1 | 9 | 95.6 | 0 | 0/0 |
| 2 | 367.5 | 22.89 | 34.18 | 32.7 | 54.8 | 172.0 | 2 | 2/0 | 7 | 89.6 | 0 | 0/0 |
| 3 | 368.6 | 22.56 | 34.18 | 31.5 | 101.1 | 181.0 | 2 | 4/0 | 10 | 118.85 | 0 | 0/0 |
| 4 | 351.6 | 23.62 | 34.18 | 36.0 | 22.7 | 153.0 | 0 | 0/0 | 5 | 32.6 | 0 | 0/0 |
| 5 | 372.2 | 22.04 | 34.18 | 30.2 | 69.9 | 176.0 | 2 | 4/1 | 15 | 131.0 | 0 | 0/0 |
| 6 | 367.4 | 22.86 | 34.18 | 33.5 | 59.3 | 151.0 | 2 | 2/0 | 6 | 68.35 | 0 | 0/0 |
| 7 | 360.3 | 22.73 | 34.18 | 32.6 | 64.4 | 156.0 | 0 | 0/0 | 7 | 93.85 | 0 | 0/0 |
| 8 | 382.1 | 22.11 | 34.18 | 29.5 | 60.5 | 173.0 | 1 | 3/1 | 7 | 140.45 | 0 | 0/0 |
| 9 | 352.1 | 23.48 | 34.18 | 34.5 | 68.8 | 164.0 | 0 | 1/0 | 7 | 112.7 | 0 | 0/0 |
| 10 | 379.7 | 21.94 | 34.18 | 28.1 | 90.2 | 180.0 | 2 | 5/2 | 9 | 196.96 | 0 | 0/0 |
| 11 | 345.7 | 24.15 | 34.18 | 38.3 | 32.1 | 153.0 | 0 | 1/0 | 4 | 69.25 | 0 | 0/0 |
| 12 | 375.3 | 22.03 | 34.18 | 29.9 | 89.5 | 175.0 | 1 | 3/0 | 6 | 161.61 | 0 | 0/0 |
| 13 | 364.6 | 23.1 | 34.18 | 33.0 | 73.1 | 161.0 | 1 | 1/1 | 9 | 97.35 | 0 | 0/0 |
| 14 | 372.3 | 22.39 | 34.18 | 28.7 | 93.8 | 182.0 | 2 | 4/0 | 11 | 113.0 | 0 | 0/0 |
| 15 | 369.1 | 22.67 | 34.18 | 30.5 | 102.7 | 174.0 | 2 | 5/1 | 6 | 135.0 | 0 | 0/0 |
| 16 | 369.6 | 22.42 | 34.18 | 31.6 | 98.4 | 167.0 | 1 | 6/0 | 6 | 110.85 | 0 | 0/0 |
| 17 | 375.1 | 21.9 | 34.18 | 29.8 | 92.6 | 161.0 | 1 | 9/0 | 6 | 74.95 | 0 | 0/0 |
| 18 | 376.0 | 22.07 | 34.18 | 29.0 | 109.6 | 180.0 | 1 | 9/2 | 3 | 103.3 | 0 | 0/0 |
| 19 | 371.2 | 22.69 | 34.18 | 31.7 | 110.6 | 157.0 | 3 | 6/2 | 9 | 89.6 | 0 | 0/0 |

Defense outcomes / containment: held=14.00, late=22.00, alongside=24.00, occupied=25.00, threat_clear=1.00, lost_speed=56.00, too_wide=0.00, risk=0.00, incidents=548.00, secondary=12.00, incident_clear_sum=421.40, recovery_sum=1456.65, clears=548.00, recoveries=252.00.
Mean cleared episode 0.77s; mean completed recovery 5.78s. Unresolved episodes/recoveries are excluded from these means. Incident count means per-NPC low-speed obstruction episodes, not unique crashes.

Abort totals: occupied=29, corner=0, guidance=0, speed_loss=0, timeout=31, contact_risk=0, rival_unavailable=1.
Corner/guidance/speed-loss outcomes remain zero when there is no explicit cancellation for that reason; speed limits are recorded separately.

### Captured scenarios and outcomes

```
CONTAIN_FIELD longest_multi_queue_s=4.10
BATTLE racer1 defenses=9 alongside_s=95.60 losses=0 repass_attempts=0 repass_completed=0 completed=1 occupied=6 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer1 held=1 late=1 alongside=3 occupied=0 threat_clear=0 lost_speed=4 too_wide=0 risk=0 incidents=37 secondary=0 longest_queue=2.45 incident_clear_sum=26.05 recovery_sum=66.55 clears=37 recoveries=12
BATTLE racer2 defenses=7 alongside_s=89.60 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=2 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer2 held=1 late=1 alongside=2 occupied=1 threat_clear=0 lost_speed=2 too_wide=0 risk=0 incidents=20 secondary=1 longest_queue=7.45 incident_clear_sum=19.00 recovery_sum=43.00 clears=20 recoveries=9
BATTLE racer3 defenses=10 alongside_s=118.85 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=2 corner=0 guidance=0 speed_loss=0 timeout=2 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer3 held=3 late=1 alongside=1 occupied=1 threat_clear=0 lost_speed=4 too_wide=0 risk=0 incidents=33 secondary=1 longest_queue=2.20 incident_clear_sum=25.00 recovery_sum=104.65 clears=33 recoveries=18
BATTLE racer4 defenses=5 alongside_s=32.60 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=0 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer4 held=0 late=2 alongside=1 occupied=2 threat_clear=0 lost_speed=0 too_wide=0 risk=0 incidents=5 secondary=0 longest_queue=1.05 incident_clear_sum=3.50 recovery_sum=17.25 clears=5 recoveries=4
BATTLE racer5 defenses=15 alongside_s=131.00 losses=0 repass_attempts=0 repass_completed=0 completed=1 occupied=1 corner=0 guidance=0 speed_loss=0 timeout=2 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer5 held=1 late=0 alongside=3 occupied=3 threat_clear=0 lost_speed=8 too_wide=0 risk=0 incidents=29 secondary=1 longest_queue=3.90 incident_clear_sum=30.25 recovery_sum=76.35 clears=29 recoveries=13
BATTLE racer6 defenses=6 alongside_s=68.35 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=0 corner=0 guidance=0 speed_loss=0 timeout=2 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer6 held=0 late=2 alongside=2 occupied=1 threat_clear=0 lost_speed=1 too_wide=0 risk=0 incidents=23 secondary=1 longest_queue=1.40 incident_clear_sum=10.80 recovery_sum=82.75 clears=23 recoveries=14
BATTLE racer7 defenses=7 alongside_s=93.85 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=0 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer7 held=1 late=0 alongside=0 occupied=0 threat_clear=0 lost_speed=6 too_wide=0 risk=0 incidents=21 secondary=0 longest_queue=1.50 incident_clear_sum=16.85 recovery_sum=70.10 clears=21 recoveries=12
BATTLE racer8 defenses=7 alongside_s=140.45 losses=0 repass_attempts=0 repass_completed=0 completed=1 occupied=1 corner=0 guidance=0 speed_loss=0 timeout=1 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer8 held=0 late=0 alongside=0 occupied=5 threat_clear=0 lost_speed=2 too_wide=0 risk=0 incidents=30 secondary=0 longest_queue=4.30 incident_clear_sum=22.00 recovery_sum=81.35 clears=30 recoveries=13
BATTLE racer9 defenses=7 alongside_s=112.70 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=0 corner=0 guidance=0 speed_loss=0 timeout=1 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer9 held=2 late=1 alongside=0 occupied=1 threat_clear=0 lost_speed=3 too_wide=0 risk=0 incidents=23 secondary=0 longest_queue=1.75 incident_clear_sum=14.55 recovery_sum=90.10 clears=23 recoveries=13
BATTLE racer10 defenses=9 alongside_s=196.96 losses=0 repass_attempts=0 repass_completed=0 completed=2 occupied=2 corner=0 guidance=0 speed_loss=0 timeout=1 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer10 held=2 late=0 alongside=1 occupied=0 threat_clear=0 lost_speed=6 too_wide=0 risk=0 incidents=28 secondary=0 longest_queue=3.45 incident_clear_sum=23.75 recovery_sum=116.35 clears=28 recoveries=17
BATTLE racer11 defenses=4 alongside_s=69.25 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=1 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer11 held=0 late=2 alongside=1 occupied=1 threat_clear=0 lost_speed=0 too_wide=0 risk=0 incidents=4 secondary=0 longest_queue=1.05 incident_clear_sum=3.00 recovery_sum=12.60 clears=4 recoveries=4
BATTLE racer12 defenses=6 alongside_s=161.61 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=1 corner=0 guidance=0 speed_loss=0 timeout=2 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer12 held=0 late=1 alongside=0 occupied=3 threat_clear=0 lost_speed=2 too_wide=0 risk=0 incidents=37 secondary=1 longest_queue=1.65 incident_clear_sum=36.20 recovery_sum=78.35 clears=37 recoveries=17
BATTLE racer13 defenses=9 alongside_s=97.35 losses=0 repass_attempts=0 repass_completed=0 completed=1 occupied=0 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer13 held=0 late=2 alongside=3 occupied=3 threat_clear=0 lost_speed=1 too_wide=0 risk=0 incidents=22 secondary=1 longest_queue=1.50 incident_clear_sum=19.35 recovery_sum=76.80 clears=22 recoveries=13
BATTLE racer14 defenses=11 alongside_s=113.00 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=1 corner=0 guidance=0 speed_loss=0 timeout=3 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer14 held=2 late=4 alongside=2 occupied=2 threat_clear=0 lost_speed=1 too_wide=0 risk=0 incidents=25 secondary=1 longest_queue=1.40 incident_clear_sum=18.65 recovery_sum=73.65 clears=25 recoveries=11
BATTLE racer15 defenses=6 alongside_s=135.00 losses=0 repass_attempts=0 repass_completed=0 completed=1 occupied=2 corner=0 guidance=0 speed_loss=0 timeout=2 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer15 held=0 late=2 alongside=0 occupied=1 threat_clear=0 lost_speed=3 too_wide=0 risk=0 incidents=31 secondary=2 longest_queue=1.70 incident_clear_sum=22.90 recovery_sum=101.20 clears=31 recoveries=14
BATTLE racer16 defenses=6 alongside_s=110.85 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=2 corner=0 guidance=0 speed_loss=0 timeout=3 contact_risk=0 rival_unavailable=1 hidden=1
CONTAIN racer16 held=0 late=1 alongside=1 occupied=0 threat_clear=0 lost_speed=4 too_wide=0 risk=0 incidents=48 secondary=1 longest_queue=1.95 incident_clear_sum=38.10 recovery_sum=67.65 clears=48 recoveries=14
BATTLE racer17 defenses=6 alongside_s=74.95 losses=0 repass_attempts=0 repass_completed=0 completed=0 occupied=2 corner=0 guidance=0 speed_loss=0 timeout=7 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer17 held=0 late=1 alongside=1 occupied=0 threat_clear=0 lost_speed=4 too_wide=0 risk=0 incidents=56 secondary=1 longest_queue=1.05 incident_clear_sum=32.45 recovery_sum=79.15 clears=56 recoveries=17
BATTLE racer18 defenses=3 alongside_s=103.30 losses=0 repass_attempts=0 repass_completed=0 completed=2 occupied=2 corner=0 guidance=0 speed_loss=0 timeout=5 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer18 held=0 late=1 alongside=0 occupied=0 threat_clear=0 lost_speed=2 too_wide=0 risk=0 incidents=44 secondary=0 longest_queue=1.65 incident_clear_sum=29.85 recovery_sum=97.85 clears=44 recoveries=19
BATTLE racer19 defenses=9 alongside_s=89.60 losses=0 repass_attempts=0 repass_completed=0 completed=2 occupied=4 corner=0 guidance=0 speed_loss=0 timeout=0 contact_risk=0 rival_unavailable=0 hidden=1
CONTAIN racer19 held=1 late=0 alongside=3 occupied=1 threat_clear=1 lost_speed=3 too_wide=0 risk=0 incidents=32 secondary=1 longest_queue=1.55 incident_clear_sum=29.15 recovery_sum=120.95 clears=32 recoveries=18
DEFENSE_CAP held=1 late=0 alongside=0 min_kmh=54.68 movement_cm=188.33 delay_s=1.35 contacts=0
SIDE min_kmh=41.02 contacts=0 alongside_s=3.00 defenses=0
REPASS losses=1 attempts=1 completed=1 contacts=0
CLEAR speed_kmh=54.85 t90=4.75 d90_cm=3288 t95=5.00 d95_cm=3643
EXIT120 apex_kmh=25.38 one=35.86 two=46.33 three=54.32 t90=2.35 d90_cm=2427 t95=2.60 d95_cm=2781 contacts=0
EXIT210 apex_kmh=25.38 one=35.86 two=46.33 three=54.32 t90=2.35 d90_cm=2446 t95=2.60 d95_cm=2799 contacts=0
EXIT300 apex_kmh=25.38 one=35.86 two=46.33 three=51.51 t90=2.35 d90_cm=2456 t95=2.60 d95_cm=2812 contacts=0
TRAIN0 min_kmh=38.88 final_kmh=54.68 contacts=0 ahead_cm=-1.0 closing_cms=0.0 peak_mph=34.18 moving_avg_mph=29.61 under20_pct=0.0 under25_pct=28.5 over30_pct=50.0 traffic_s=0.0 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=1 brake_s=0.1 longest_queue_s=0.0
TRAIN1 min_kmh=40.26 final_kmh=54.72 contacts=0 ahead_cm=-1.0 closing_cms=0.0 peak_mph=34.18 moving_avg_mph=31.53 under20_pct=0.0 under25_pct=0.0 over30_pct=69.0 traffic_s=2.8 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=1 brake_s=0.1 longest_queue_s=0.0
TRAIN2 min_kmh=40.57 final_kmh=54.94 contacts=0 ahead_cm=495.6 closing_cms=-2.7 peak_mph=34.18 moving_avg_mph=30.74 under20_pct=0.0 under25_pct=0.0 over30_pct=54.5 traffic_s=5.5 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=0 brake_s=0.0 longest_queue_s=0.0
TRAIN3 min_kmh=41.15 final_kmh=54.77 contacts=0 ahead_cm=456.3 closing_cms=-4.8 peak_mph=34.18 moving_avg_mph=30.84 under20_pct=0.0 under25_pct=0.0 over30_pct=52.5 traffic_s=5.8 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=0 brake_s=0.0 longest_queue_s=0.0
TRAIN4 min_kmh=41.79 final_kmh=54.94 contacts=0 ahead_cm=452.5 closing_cms=4.8 peak_mph=34.18 moving_avg_mph=30.94 under20_pct=0.0 under25_pct=0.0 over30_pct=56.0 traffic_s=6.1 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=0 brake_s=0.0 longest_queue_s=0.0
TRAIN5 min_kmh=42.50 final_kmh=54.77 contacts=0 ahead_cm=449.6 closing_cms=-4.8 peak_mph=34.18 moving_avg_mph=31.06 under20_pct=0.0 under25_pct=0.0 over30_pct=59.0 traffic_s=6.3 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=0 brake_s=0.0 longest_queue_s=0.0
PASS success=1 flips=0 contacts=0 emergency=0 final_kmh=54.77 attempts=1 completed=1
RELEASE blocked_cms=188.3 clear_cms=1527.8 after_s=2
INCIDENT_NPC one_side=0 npc=1 passed=1 min_kmh=8.68 contacts=0 recovered_at_s=6.85 queue_s=0.25 clear_to_90pct_s=2.60
INCIDENT_NPC one_side=0 npc=2 passed=1 min_kmh=7.89 contacts=0 recovered_at_s=6.45 queue_s=0.35 clear_to_90pct_s=1.75
INCIDENT_NPC one_side=0 npc=3 passed=1 min_kmh=0.00 contacts=0 recovered_at_s=18.35 queue_s=7.50 clear_to_90pct_s=2.60
INCIDENT_NPC one_side=0 npc=4 passed=1 min_kmh=8.68 contacts=0 recovered_at_s=9.15 queue_s=1.30 clear_to_90pct_s=1.50
INCIDENT_NPC one_side=0 npc=5 passed=1 min_kmh=7.18 contacts=0 recovered_at_s=10.55 queue_s=0.65 clear_to_90pct_s=1.80
INCIDENT_NPC one_side=0 npc=6 passed=1 min_kmh=7.36 contacts=0 recovered_at_s=9.60 queue_s=1.10 clear_to_90pct_s=0.90
INCIDENT_NPC one_side=0 npc=7 passed=1 min_kmh=6.70 contacts=0 recovered_at_s=12.70 queue_s=0.45 clear_to_90pct_s=2.05
INCIDENT_NPC one_side=0 npc=8 passed=1 min_kmh=7.52 contacts=0 recovered_at_s=16.05 queue_s=1.80 clear_to_90pct_s=2.35
INCIDENT_NPC one_side=0 npc=9 passed=1 min_kmh=0.00 contacts=0 recovered_at_s=22.75 queue_s=2.50 clear_to_90pct_s=3.55
INCIDENT one_side=0 passed=9 expected=9 contacts=0 clear_s=19.20 left=6 right=8 min_kmh=0.00
INCIDENT_NPC one_side=1 npc=2 passed=1 min_kmh=7.89 contacts=0 recovered_at_s=6.25 queue_s=0.05 clear_to_90pct_s=1.70
INCIDENT_NPC one_side=1 npc=3 passed=1 min_kmh=0.49 contacts=0 recovered_at_s=9.65 queue_s=1.15 clear_to_90pct_s=2.65
INCIDENT_NPC one_side=1 npc=4 passed=1 min_kmh=0.00 contacts=0 recovered_at_s=18.50 queue_s=4.70 clear_to_90pct_s=2.15
INCIDENT_NPC one_side=1 npc=5 passed=1 min_kmh=8.56 contacts=0 recovered_at_s=9.65 queue_s=0.80 clear_to_90pct_s=1.65
INCIDENT_NPC one_side=1 npc=6 passed=1 min_kmh=0.00 contacts=0 recovered_at_s=30.15 queue_s=5.30 clear_to_90pct_s=2.80
INCIDENT_NPC one_side=1 npc=7 passed=1 min_kmh=8.68 contacts=0 recovered_at_s=9.80 queue_s=0.45 clear_to_90pct_s=1.30
INCIDENT_NPC one_side=1 npc=8 passed=1 min_kmh=7.69 contacts=0 recovered_at_s=9.45 queue_s=1.80 clear_to_90pct_s=0.40
INCIDENT_NPC one_side=1 npc=9 passed=1 min_kmh=7.51 contacts=0 recovered_at_s=10.10 queue_s=1.75 clear_to_90pct_s=0.05
INCIDENT one_side=1 passed=8 expected=8 contacts=0 clear_s=27.35 left=1 right=8 min_kmh=0.00
20-kart 8s launch: contacts 0, first-second lane drift 0.1 cm
```
