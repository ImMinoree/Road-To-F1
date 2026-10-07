#pragma once

#include "CoreMinimal.h"

/** Deterministic single-player race rules. Time is supplied by the world (pauses stop it). */
struct FRaceProgress
{
    int32 TargetLaps = 3;
    int32 CheckpointCount = 3;
    int32 CompletedLaps = 0;
    int32 NextCheckpoint = 0;
    bool bStarted = false;
    bool bFinished = false;
    double RaceStart = 0;
    double LapStart = 0;
    double FinishTime = 0;
    TArray<double> LapTimes;

    void Reset(int32 InTargetLaps, int32 InCheckpointCount)
    {
        *this = FRaceProgress();
        TargetLaps = FMath::Max(1, InTargetLaps);
        CheckpointCount = FMath::Max(1, InCheckpointCount);
    }

    // Gate 0 is start/finish; checkpoint gates are numbered 1..CheckpointCount.
    bool CrossGate(int32 Gate, double Now, bool bForward = true)
    {
        if (!bForward || bFinished || Gate < 0 || Gate > CheckpointCount) return false;
        if (!bStarted)
        {
            if (Gate != 0) return false;
            bStarted = true;
            RaceStart = LapStart = Now;
            return true;
        }
        if (Gate > 0)
        {
            if (Gate != NextCheckpoint + 1) return false;
            ++NextCheckpoint;
            return true;
        }
        if (NextCheckpoint != CheckpointCount) return false;
        LapTimes.Add(FMath::Max(0.0, Now - LapStart));
        ++CompletedLaps;
        NextCheckpoint = 0;
        LapStart = Now;
        if (CompletedLaps >= TargetLaps)
        {
            bFinished = true;
            FinishTime = Now;
        }
        return true;
    }

    int32 CurrentLap() const { return bStarted ? FMath::Min(CompletedLaps + 1, TargetLaps) : 0; }
    double TotalTime(double Now) const { return bStarted ? FMath::Max(0.0, (bFinished ? FinishTime : Now) - RaceStart) : 0; }
    double LapTime(double Now) const { return bFinished ? LapTimes.Last() : (bStarted ? FMath::Max(0.0, Now - LapStart) : 0); }
};

/** Swept gate plane test, independent of collision events or the number of vehicle components. */
struct FRaceGateGeometry
{
    FTransform Transform;
    FVector Extent = FVector(100, 1200, 300);

    bool ForwardCrossing(const FVector& Previous, const FVector& Current, double& Fraction) const
    {
        const FVector A = Transform.InverseTransformPosition(Previous);
        const FVector B = Transform.InverseTransformPosition(Current);
        if (A.X >= 0 || B.X < 0) return false;
        Fraction = -A.X / (B.X - A.X);
        const FVector Hit = FMath::Lerp(A, B, Fraction);
        return FMath::Abs(Hit.Y) <= Extent.Y && FMath::Abs(Hit.Z) <= Extent.Z;
    }
};
