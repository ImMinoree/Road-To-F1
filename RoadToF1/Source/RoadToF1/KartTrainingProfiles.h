#pragma once
#include "CoreMinimal.h"

struct FKartTrainingStyle
{
    float Aggression = .6f, CornerSkill = .98f, PreferredLane = 0, DecisionSeconds = 2.5f;
};

/** Aggregate tendencies only: no recorded route or input sequence is a policy. */
struct ROADTOF1_API FKartTrainingProfiles
{
    static bool Parse(const FString& Json, const FString& Track, TArray<FKartTrainingStyle>& Out);
};
