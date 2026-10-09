#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "KartTrainingRecorder.generated.h"

/** Opt-in local capture; native aggregate learner also compiles in packaged games. */
UCLASS()
class ROADTOF1_API UKartTrainingRecorder : public UActorComponent
{
    GENERATED_BODY()
public:
    UKartTrainingRecorder();
    virtual void TickComponent(float Dt, ELevelTick TickType, FActorComponentTickFunction* TickFunction) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    bool StartCapture();
    void StopCapture();
    void ToggleCapture();
    void RestartSessionIfActive();
    bool IsRecording() const { return bRecording; }
    const FString& GetCapturePath() const { return CapturePath; }
    const FString& GetCandidatePath() const { return CandidatePath; }
    int32 GetSampleCount() const { return SampleCount; }
private:
    void Sample();
    bool Flush();
    void WriteCandidate();
    bool bRecording = false;
    FString CapturePath, CandidatePath, SessionId, TrackId, Buffer;
    double Elapsed = 0, LastSample = 0;
    int32 SampleCount = 0, CleanSamples = 0, CornerSamples = 0, StraightSamples = 0, PreviousContacts = 0;
    double SumSpeed = 0, SumThrottle = 0, SumLane = 0, SumCornerSpeed = 0;
};
