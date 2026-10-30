#pragma once

// Shared race defaults. SI solver and Unreal presentation use the same ceiling.
namespace KartRace {
constexpr int KartCount=20, OpponentCount=KartCount-1, PlayerGridPosition=10;
constexpr double TopSpeedMph=38.0;
constexpr double TopSpeedMps=TopSpeedMph*.44704;
constexpr double TopSpeedCmps=TopSpeedMps*100.0;
}
