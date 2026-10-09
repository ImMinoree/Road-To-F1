# Road-To-F1
Unreal Engine racing game: begin in karting and work toward Formula 1.

Open the original project at `RoadToF1/RoadToF1.uproject` using Unreal Engine **5.8.3**. On the gaming-lab PC, the editor is `D:/Boring/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe`.

The playable map is `/Game/RoadToF1/SouthGarda_KartRace`. W accelerates, S brakes/reverses, A/D steer, Space brakes, and F5 resets the field and race. There are 19 opponents; speed limits are 57 km/h for the player and 55 km/h for opponents.

Use only the original `RoadToF1` folder. After comparison, the engine-created duplicate was retired outside the repository to `D:/Boring/RaceValidation/RetiredProjects/RoadToF1-5.8-20261009` as a recovery backup.

NPC training starts with optional local gameplay telemetry: **F9** starts/stops recording; files are saved under `RoadToF1/Saved/Training/Telemetry/`. The native aggregate learner creates experimental candidate styles only with adequate clean corner/straight coverage. Candidates never install themselves. The modular offline toolkit and evaluation workflow are in [AI Agent for game training](AI%20Agent%20for%20game%20training/README.md). Recording stays off by default; future signup consent and Steam release packaging are separate milestones.
