#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "RaceProgress.h"
#include "RaceLoopSubsystem.generated.h"

class APawn;
class APlayerController;
class UInputComponent;
class URaceLoopWidget;

/** Prototype-only integration: leaves the user's map and Blueprint assets unchanged. */
UCLASS(Config=Game)
class ROADTOF1_API URaceLoopSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()
public:
    virtual void OnWorldBeginPlay(UWorld& InWorld) override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override { RETURN_QUICK_DECLARE_CYCLE_STAT(URaceLoopSubsystem, STATGROUP_Tickables); }
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category="Race")
    void RestartRace();

    const FRaceProgress& GetProgress() const { return Progress; }
    const TArray<FRaceGateGeometry>& GetGates() const { return Gates; }
    bool IsRaceAvailable() const { return bReady; }
    const FString& GetStatusMessage() const { return StatusMessage; }

protected:
    virtual bool DoesSupportWorldType(EWorldType::Type Type) const override;

    UPROPERTY(Config)
    int32 TargetLaps = 3;
    UPROPERTY(Config)
    TArray<FVector> CheckpointLocations;
    UPROPERTY(Config)
    TArray<float> CheckpointYaw;

private:
    void DiscoverTrack();
    void AttachPlayer();
    void RefreshGateMarkers();
    FRaceProgress Progress;
    TArray<FRaceGateGeometry> Gates;
    bool bReady = false;
    bool bHavePreviousPosition = false;
    FVector PreviousPosition = FVector::ZeroVector;
    double PreviousTime = 0;
    FTransform RestartTransform;
    FString StatusMessage = TEXT("Waiting for the start/finish trigger...");
    TWeakObjectPtr<APawn> TrackedPawn;
    TWeakObjectPtr<APlayerController> AttachedController;
    UPROPERTY(Transient)
    TObjectPtr<URaceLoopWidget> RaceWidget;
    UPROPERTY(Transient)
    TObjectPtr<UInputComponent> RaceInput;
    UPROPERTY(Transient)
    TArray<TObjectPtr<AActor>> GateMarkers;
};
