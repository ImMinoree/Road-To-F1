#pragma once
#include "CoreMinimal.h"

/** Local mono two-stroke approximation. No recordings or network service required. */
struct FKartEngineSound
{
    static constexpr int32 SampleRate = 22050;
    double Phase = 0;
    float Frequency = 50;
    void Render(TArray<int16>& Samples, int32 Count, float SpeedRatio, float Throttle, bool bDisabled, int32 Number)
    {
        Samples.SetNumUninitialized(Count);
        const float Target = 50.f + 130.f * FMath::Clamp(SpeedRatio, 0.f, 1.f) + 20.f * FMath::Abs(Throttle);
        for (int32 I = 0; I < Count; ++I)
        {
            Frequency += (Target - Frequency) * .0004f;
            Phase = FMath::Fmod(Phase + Frequency / SampleRate, 1.);
            const double Angle = Phase * 2 * PI;
            const float Pulse = FMath::Sin(Angle) + .5f * FMath::Sin(Angle * 2 + Number * .13) + .22f * FMath::Sin(Angle * 5);
            Samples[I] = bDisabled ? 0 : FMath::Clamp(FMath::RoundToInt(Pulse * 10000), -32767, 32767);
        }
    }
};
