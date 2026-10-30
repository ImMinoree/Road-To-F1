#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/GameModeBase.h"
#include "ProofPawn.generated.h"
class UKartMechanicalVisuals; class UCameraComponent; class UBoxComponent; class ARaceStartGantry; class AGridStartSlot; class ULocalKartDriverVisuals; class UTrackRacingAI; class UKartSurfaceFX; class UKartTireDynamics;
class USpringArmComponent; class UStaticMeshComponent; class USkeletalMeshComponent;
UENUM(BlueprintType)
enum class ERaceStartPhase : uint8 { PreGrid, Countdown, AllRed, LightsOut, Racing };
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FRaceLightsOutEvent,double,StartWorldSeconds);
// Fixed-step tire forces with Unreal swept collision; legacy movement is an explicit fallback.
UCLASS()
class ROAD_TO_F1_NEW_API AProofPawn : public APawn {
 GENERATED_BODY()
public:
 AProofPawn();
 UFUNCTION(BlueprintCallable,Category="Kart camera") void ToggleCameraView();
 UFUNCTION(BlueprintPure,Category="Kart camera") bool IsThirdPersonView()const{return bThirdPersonView;}
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart grid",meta=(ClampMin="0",ClampMax="20")) int32 PreferredGridPosition=0;
 UPROPERTY(BlueprintReadOnly,Category="Kart grid") int32 AssignedGridPosition=0;
 virtual void Tick(float DeltaSeconds) override;
 virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
 void StageForRace(const FTransform& GridTransform);
 void ConfigureRacingAI(int32 GridPosition);
 void SetAutonomousInput(float InThrottle,float InSteer);
 void SetAutonomousControls(float InThrottle,float InSteer,float ServiceBrake);
 void SetRacingDiagnosticControls(float InThrottle,float InSteer,float ServiceBrake);
 void SetRacingDiagnosticInput(float InThrottle,float InSteer);
 float GetDrivingSpeed() const;
 float GetVisualThrottle() const { return Throttle; }
 float GetVisualBrake() const { return bBrakeHeld?1.f:0.f; }
 virtual FVector GetVelocity()const override;
 UKartTireDynamics* GetTireDynamics()const{return TireDynamics;}
 float GetSteeringVisualInput()const;
 float SteeringForCurvature(float CurvatureCm)const;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart dynamics") bool bUseTireDynamics=true;
 /** Explicit development test input only; inactive without -KartDynamicsTest. */
 UFUNCTION(BlueprintCallable,Category="Kart diagnostics") void SetKartTestInput(float InThrottle,float InSteer,bool bBrake);
 /** Shared by human and AI: maximum yaw rate at the existing 1600 cm/s speed reference. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart driving",meta=(ClampMin="30",ClampMax="360")) float SteeringYawRateAtTopSpeed=240.f;
 float GetSteeringYawRate() const {return FMath::Clamp(SteeringYawRateAtTopSpeed,30.f,360.f);}
 float GetMaximumSteeringCurvature() const;
 UPROPERTY(BlueprintReadOnly,Category="Racing AI") bool bRacingAI=false;
private:
 UPROPERTY() UBoxComponent* Body;
 UPROPERTY() UCameraComponent* Camera;
 UPROPERTY(VisibleAnywhere,Category="Kart camera") TObjectPtr<USpringArmComponent> ChaseArm;
 UPROPERTY(VisibleAnywhere,Category="Kart camera") TObjectPtr<UCameraComponent> ChaseCamera;
 UPROPERTY(Transient) TObjectPtr<UStaticMeshComponent> ExteriorChassis;
 UPROPERTY(Transient) TObjectPtr<USkeletalMeshComponent> ExteriorDriver;
 UPROPERTY(Transient) TObjectPtr<UStaticMeshComponent> ExteriorWheel;
 bool bThirdPersonView=false;
 bool CreateExteriorVisuals();
 void UpdateExteriorSteering();
 UPROPERTY(VisibleAnywhere,Category="Player visuals") TObjectPtr<UKartMechanicalVisuals> MechanicalVisuals;
 UPROPERTY(VisibleAnywhere,Category="Player visuals") TObjectPtr<ULocalKartDriverVisuals> LocalDriverVisuals;
 UPROPERTY(VisibleAnywhere,Category="Surface effects") TObjectPtr<UKartSurfaceFX> SurfaceFX;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Kart dynamics",meta=(AllowPrivateAccess="true")) TObjectPtr<UKartTireDynamics> TireDynamics;
 bool bBrakeHeld=false;
#if !UE_BUILD_SHIPPING
 bool bKartTestInputActive=false,bKartTestBrake=false;
 float KartTestThrottle=0,KartTestSteering=0;
#endif
 void BrakePressed(){bBrakeHeld=true;}
 void BrakeReleased(){bBrakeHeld=false;}
 float Throttle=0,Steer=0,Speed=0;
 float TestTime=0,SampleTime=0; int32 SampleFrames=0;
 void TickIntegrationEvidence();
 int32 IntegrationCaptureStage=0;
 FVector IntegrationGridPosition=FVector::ZeroVector;
 bool bIntegrationMovedEarly=false;
 bool bIntegrationGridCaptured=false;
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
 double CountdownCueWorldSeconds=-1; // Latest authoritative RED_ON timestamp, for the local HUD fade.
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
 UPROPERTY(VisibleAnywhere,Category="Racing AI") TObjectPtr<UTrackRacingAI> RacingAI;
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



