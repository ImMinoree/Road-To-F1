Measured standalone Unreal Editor game session, 2026-10-20. NVIDIA RTX 3080 (10053 MB dedicated VRAM), Intel i7-10700KF, 31.9 GB RAM, D3D12 SM6. Original unrelated Unreal Editor remained open.

1920×1080 window, Balanced: scalability 2, 75% internal resolution, TSR, software Lumen, conventional shadows, VSync/frame cap off. After the first 10 seconds, 2249 frames over 10.0047 seconds: **4.449 ms average / 224.79 FPS** from FApp frame intervals. Raw output: Runtime.json. This is an incomplete, almost empty environment with no kart art, vegetation or AI. It does not predict the final game's performance or a 20-kart race. No individual GPU pass timings were captured.

The bounded test loaded ProofGameMode, spawned the temporary pawn, applied acceleration/steering/braking inputs and exited normally. Final pawn position: (3842.09, -2.62, 31.00) cm versus start (800, 0, 31) cm; movement and road-height following occurred. This is a movement smoke check, not a kart-physics or race validation.

Validation captures used Epic (3), full internal resolution and VSM; their performance was not benchmarked. CaptureFinal.log records a VSM non-Nanite marking queue overflow; Balanced disables VSM based on this observation. These profiles require remeasurement with production art.
