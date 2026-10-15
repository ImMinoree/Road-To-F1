#pragma once
#include "CoreMinimal.h"

/** One clock and two opacity envelopes. Retriggers extend holds, never stack timers. */
struct FRaceHUDVisibility
{
    double LastTime = 0, LeaderUntil = 0, BriefUntil = 0, NextPeriodic = 0;
    float LeaderAlpha = 0, BriefAlpha = 0;
    int32 LastPlace = -1;
    bool bWasStarted = false, bWasFinished = false;
    void Reset(double Now)
    {
        LastTime = Now; LeaderUntil = Now + 5; BriefUntil = Now + 6;
        NextPeriodic = TNumericLimits<double>::Max();
        LeaderAlpha = BriefAlpha = 0; LastPlace = -1;
        bWasStarted = bWasFinished = false;
    }
    void Update(double Now, bool bStarted, int32 Place, bool bTab, bool bFinished)
    {
        if (Now < LastTime) Reset(Now);
        if (bStarted && !bWasStarted)
        {
            LeaderUntil = Now + 5; BriefUntil = Now + 6; NextPeriodic = Now + 20;
        }
        if (bStarted && !bFinished && Now >= NextPeriodic)
        {
            LeaderUntil = FMath::Max(LeaderUntil, Now + 3);
            NextPeriodic += (FMath::FloorToDouble((Now - NextPeriodic) / 20) + 1) * 20;
        }
        if (bStarted && LastPlace > 0 && Place != LastPlace) LeaderUntil = FMath::Max(LeaderUntil, Now + 3);
        if (bFinished && !bWasFinished) LeaderUntil = FMath::Max(LeaderUntil, Now + 6);
        auto Advance = [this, Now](float Alpha, double Until, bool bForced)
        {
            const float Rise = float(FMath::Max(0., (bForced ? Now : FMath::Min(Now, Until)) - LastTime));
            const float Fall = bForced ? 0.f : float(FMath::Max(0., Now - FMath::Max(LastTime, Until)));
            return FMath::Clamp(FMath::Clamp(Alpha + Rise * 4, 0.f, 1.f) - Fall, 0.f, 1.f);
        };
        // Tab never changes the automatic deadlines, so release resumes their current state.
        LeaderAlpha = Advance(LeaderAlpha, LeaderUntil, bTab);
        BriefAlpha = Advance(BriefAlpha, BriefUntil, false);
        LastTime = Now; LastPlace = Place; bWasStarted = bStarted; bWasFinished = bFinished;
    }
    static int32 FirstRow(int32 Place, int32 Count, bool bFull)
    {
        return bFull ? 0 : FMath::Clamp(Place - 1 - 3, 0, FMath::Max(0, Count - 7));
    }
};
