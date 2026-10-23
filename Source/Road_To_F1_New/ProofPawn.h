#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/GameModeBase.h"
#include "ProofPawn.generated.h"
class UCameraComponent; class USphereComponent; class ARaceStartGantry; class AGridStartSlot; class ULocalKartDriverVisuals;
UENUM(BlueprintType)
enum class ERaceStartPhase : uint8 { PreGrid, Countdown, AllRed, LightsOut, Racing };
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FRaceLightsOutEvent,double,StartWorldSeconds);
// Temporary swept kinematic driving. No production kart physics or cockpit claims.
UCLASS()
class ROAD_TO_F1_NEW_API AProofPawn : public APawn {
 GENERATED_BODY()
public:
 AProofPawn();
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart grid",meta=(ClampMin="0",ClampMax="20")) int32 PreferredGridPosition=0;
 UPROPERTY(BlueprintReadOnly,Category="Kart grid") int32 AssignedGridPosition=0;
 virtual void Tick(float DeltaSeconds) override;
 virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
 void StageForRace(const FTransform& GridTransform);
private:
 UPROPERTY() USphereComponent* Body;
 UPROPERTY() UCameraComponent* Camera;
 UPROPERTY(VisibleAnywhere,Category="Player visuals") TObjectPtr<ULocalKartDriverVisuals> LocalDriverVisuals;
 float Throttle=0,Steer=0,Speed=0;
 float TestTime=0,SampleTime=0; int32 SampleFrames=0;
 void Drive(float V){Throttle=V;}
 void Turn(float V){Steer=V;}
 void Reset();
};
UCLASS()
class ROAD_TO_F1_NEW_API AProofGameMode : public AGameModeBase {
 GENERATED_BODY()
public:
 AProofGameMode();
 virtual void BeginPlay() override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 virtual AActor* ChoosePlayerStart_Implementation(AController* Player) override;
 UPROPERTY(EditDefaultsOnly,BlueprintReadWrite,Category="Race start",meta=(ClampMin="0.1")) float StagingDelay=2.f;
 UPROPERTY(EditDefaultsOnly,BlueprintReadWrite,Category="Race start",meta=(ClampMin="0.1")) float RedInterval=1.f;
 UPROPERTY(EditDefaultsOnly,BlueprintReadWrite,Category="Race start",meta=(ClampMin="0.1")) float AllRedHold=1.25f;
 UPROPERTY(EditDefaultsOnly,BlueprintReadWrite,Category="Race start") bool bShowLightsOutCue=true;
 UPROPERTY(BlueprintReadOnly,Category="Race start") ERaceStartPhase RacePhase=ERaceStartPhase::PreGrid;
 UPROPERTY(BlueprintReadOnly,Category="Race start") int32 RedLightCount=0;
 UPROPERTY(BlueprintReadOnly,Category="Race start") double RaceStartWorldSeconds=-1;
 UPROPERTY(BlueprintReadOnly,Category="Race start") int32 StartEventCount=0;
 UPROPERTY(BlueprintAssignable,Category="Race start") FRaceLightsOutEvent OnLightsOut;
 UPROPERTY(BlueprintReadOnly,Category="Kart grid") int32 StagedParticipantCount=0;
 UFUNCTION(BlueprintCallable,Category="Kart grid") bool RegisterGridParticipant(AProofPawn* Pawn,int32 RequestedPosition=0);
 UFUNCTION(BlueprintPure,Category="Kart grid") AGridStartSlot* GetGridSlotForPawn(AProofPawn* Pawn) const;
 UFUNCTION(BlueprintPure,Category="Race start") bool IsStartGateClosed() const {return bStartEnabled&&RaceStartWorldSeconds<0;}
 UFUNCTION(BlueprintPure,Category="Race start") float GetRaceElapsedSeconds() const;
 UFUNCTION(BlueprintCallable,Exec,Category="Race start") void RestartRaceStart();
private:
 UPROPERTY() TObjectPtr<ARaceStartGantry> Gantry;
 bool bStartEnabled=false,bTesting=false,bTestMovedEarly=false;
 int32 TestEpoch=0;
 FVector TestGridPosition;
 FTimerHandle ReadyTimer,SequenceTimer,TestCaptureTimer,TestControlTimer;
 TMap<TWeakObjectPtr<AProofPawn>,int32> GridAssignments;
 TMap<TWeakObjectPtr<AController>,int32> ControllerGridSlots;
 TArray<AGridStartSlot*> FindGridSlots() const;
 bool StageGridParticipants();
 FString StartEvidenceDirectory() const;
 TMap<TWeakObjectPtr<AProofPawn>,FVector> StagedPositions;
 void WaitForGrid(); void AddRed(); void ReleaseRace(); void EnterRacing();
 void Record(const TCHAR* Event); void Capture(const TCHAR* Name); void TestAfterRelease();
};


