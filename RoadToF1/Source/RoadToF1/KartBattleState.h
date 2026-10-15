#pragma once
#include "CoreMinimal.h"

enum class EKartDefense : uint8 { Normal, Holding, Released };
enum class EKartPassOutcome : uint8 { Completed, Occupied, Corner, Guidance, SpeedLoss, Timeout, ContactRisk, RivalUnavailable, Count };
enum class EKartDefenseOutcome : uint8 { None, Held, TooLate, Alongside, Occupied, ThreatCleared, LostSpeed, TrackTooWide, ContactRisk, Count };
struct FKartBattleState
{
    EKartDefense Defense = EKartDefense::Normal;
    float DefenseSeconds = 0, DefenseCooldown = 0, DefenseLane = 0;
    float DefenseElapsed = 0, DefenseMoveDelay = -1, DefenseStartLane = 0, DefenseStartSpeed = 0;
    float DefenseGap = 0, DefenseClosing = 0, DefenseMovement = 0, DefenseMinimumSpeed = 0;
    float DefenseGeometry = 1;
    bool bDefenseEligible = false;
    EKartDefenseOutcome DefenseOutcome = EKartDefenseOutcome::None;
    int32 DefenseOutcomes[int32(EKartDefenseOutcome::Count)] = {};
    void EndDefense(EKartDefenseOutcome Result)
    {
        DefenseOutcome=Result; ++DefenseOutcomes[int32(Result)]; Defense=EKartDefense::Released; DefenseCooldown=6;
    }
    float IncidentReservation = 0, IncidentLane = 0, RejoinSeconds = 0;
    int32 IncidentTarget = 0, IncidentEvents = 0, SecondaryContacts = 0, PreviousContacts = 0, IncidentClears = 0, SpeedRecoveries = 0;
    float IncidentSeconds = 0, IncidentClearSeconds = 0, SpeedRecoverySeconds = 0, RecoveryClock = -1;
    float QueueSeconds = 0, LongestQueue = 0;
    bool bIncidentActive = false, bRejoining = false;
    float PassExtension = 0;

    float PlayerAhead = 0, PlayerSide = 0, PlayerDistance = 0, PlayerClosing = 0, PlayerLane = 0;
    float RepassSeconds = 0, AlongsideSeconds = 0, FinishSeconds = 0;
    float Corridor = 0;
    bool bAlongside = false, bYielding = false, bPlayerWasAhead = false, bPlayerSeen = false, bRepassAttempt = false;
    int32 DefenseRival = 0;
    int32 Defenses = 0, PositionsLost = 0, RepassAttempts = 0, RepassCompletions = 0;
    int32 Outcomes[int32(EKartPassOutcome::Count)] = {};
    const TCHAR* Conflict = TEXT("None");
    void Outcome(EKartPassOutcome Result) { ++Outcomes[int32(Result)]; }
};
