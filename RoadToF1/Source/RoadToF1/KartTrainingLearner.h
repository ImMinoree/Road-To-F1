#pragma once
#include "CoreMinimal.h"

struct FKartDrivingSummary
{
    int32 CleanSamples = 0, CornerSamples = 0, StraightSamples = 0;
    double SumSpeed = 0, SumThrottle = 0, SumLane = 0, SumCornerSpeed = 0;
};

/** Experimental native proposal module. It never installs its output. */
struct ROADTOF1_API FKartTrainingLearner
{
    static FString Propose(const FString& Track, int32 Seed, const FKartDrivingSummary& Summary);
};
