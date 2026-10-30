# Game development process

This is my development journal for **Road To F1**. These reports describe the features I added and improved as the human project owner, using Codex for implementation, testing, and documentation assistance. They are written from my perspective and do not imply that every implementation step was performed manually without assistance.

Each report records the work at the time it was validated. Later work can change the current project; older results remain historical evidence, not a claim that every later revision has been revalidated.

| Development report | Work completed |
| --- | --- |
| [Mechanical kart and seated driver](2026-10-26-mechanical-kart-and-driver.md) | Playable visual assembly, steering linkage, wheel rolling, drivetrain and driver synchronization |
| [Gloved hand structure](2026-10-28-gloved-hand-structure.md) | Fuller palms, opposed thumbs and fingers wrapped around the original wheel |
| [Stacked tire barriers](2026-10-28-stacked-tire-barriers.md) | Editable Blender tires, modular exports, PBR materials and initial corner placement |
| [Live speed gauge](2026-10-30-live-speed-gauge.md) | Bottom-right speed arc and digital readout driven by actual movement |
| [Unreal MCP for Codex](2026-10-30-unreal-mcp-for-codex.md) | Native Unreal toolsets, automatic server startup and Codex-only connection |
| [Twenty-kart grid and AI launch](2026-10-30-twenty-kart-launch.md) | Nineteen uniquely colored opponents, full-throttle starts, measured pace and limitations |
| [AI pace and tire-wall gaps](2026-10-30-ai-pace-and-tire-gaps.md) | Clear-straight pace planning, 291 additional tire instances and historical clearance validation |

## Supporting development records

The repository also contains [navigation-map notes](../../Evidence/NavigationMap/README.txt), [race-awareness notes](../../Evidence/RaceAwareness/README.txt), [competitive-AI results](../../Evidence/CompetitiveAI/Report.md), [environment-depth notes](../../Evidence/EnvironmentDepth/README.txt), and an [outer-scenery report](../../Evidence/OuterScenery/Report.md). Those records retain their original validation scope and limitations.

## How reports are maintained

For future completed features, I want a dated report with a clear feature heading, my changes, the purpose, actual checks, screenshots where useful, and any remaining issues. The relevant report should be included in the same authorized feature commit. JSON, CSV and screenshots under `Evidence/` remain supporting records; this journal provides the readable account.

Adding a report locally, committing it, and successfully pushing it to GitHub are separate steps. A blocked or pending push is never recorded as published.
