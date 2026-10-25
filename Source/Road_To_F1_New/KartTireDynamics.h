#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "KartTireModel.h"
#include "KartTireDynamics.generated.h"
class USoundBase;class UAudioComponent;
UENUM(BlueprintType)
enum class EKartGripSurface:uint8 { Asphalt,Curb,Grass,Dirt,Unknown,Airborne };

USTRUCT(BlueprintType)
struct FKartSlipTelemetry {
 GENERATED_BODY()
 UPROPERTY(BlueprintReadOnly) float LongitudinalSpeedMps=0;
 UPROPERTY(BlueprintReadOnly) float LateralSpeedMps=0;
 UPROPERTY(BlueprintReadOnly) float SideslipDegrees=0;
 UPROPERTY(BlueprintReadOnly) float YawRateDegrees=0;
 UPROPERTY(BlueprintReadOnly) float FrontSlipDegrees=0;
 UPROPERTY(BlueprintReadOnly) float RearSlipDegrees=0;
 UPROPERTY(BlueprintReadOnly) float FrontLateralForceN=0;
 UPROPERTY(BlueprintReadOnly) float RearLateralForceN=0;
 UPROPERTY(BlueprintReadOnly) float FrontLongitudinalForceN=0;
 UPROPERTY(BlueprintReadOnly) float RearLongitudinalForceN=0;
 UPROPERTY(BlueprintReadOnly) float FrontSaturation=0;
 UPROPERTY(BlueprintReadOnly) float RearSaturation=0;
 UPROPERTY(BlueprintReadOnly) float RearLongitudinalDemand=0;
 UPROPERTY(BlueprintReadOnly) float FrontGrip=1.05f;
 UPROPERTY(BlueprintReadOnly) float RearGrip=1.05f;
 UPROPERTY(BlueprintReadOnly) float LateralAccelerationG=0;
 UPROPERTY(BlueprintReadOnly) float SteeringDegrees=0;
 UPROPERTY(BlueprintReadOnly) float RearInsideLoadFraction=.5f;
 UPROPERTY(BlueprintReadOnly) int32 GroundedWheels=0;
 UPROPERTY(BlueprintReadOnly) bool bDrifting=false;
 UPROPERTY(BlueprintReadOnly) bool bOversteering=false;
 UPROPERTY(BlueprintReadOnly) EKartGripSurface FrontSurface=EKartGripSurface::Unknown;
 UPROPERTY(BlueprintReadOnly) EKartGripSurface RearSurface=EKartGripSurface::Unknown;
};

/** Fixed-step custom force dynamics; swept world collision, no second vehicle pawn or Chaos rig. */
UCLASS(ClassGroup=(Movement),meta=(BlueprintSpawnableComponent))
class ROAD_TO_F1_NEW_API UKartTireDynamics:public UActorComponent {
 GENERATED_BODY()
public:
 UKartTireDynamics();
 virtual void BeginPlay() override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 void Simulate(float Dt,float Throttle,float Steering,bool bBrake);
 void HoldForStart(float Dt,float Steering);
 UFUNCTION(BlueprintCallable,Category="Kart dynamics") void ResetMotion();
 UFUNCTION(BlueprintPure,Category="Kart dynamics") FKartSlipTelemetry GetTelemetry()const{return Telemetry;}
 FVector GetWorldVelocity()const;
 float GetForwardSpeedCm()const{return float(State.U*100);}
 float GetSteeringVisualInput()const{return float(State.Steer/KartDynamics::Rad(Parameters().MaxSteerDegrees));}
 float GetMaximumCurvatureCm()const;
 float SteeringForCurvature(float CurvatureCm)const;
 KartDynamics::Parameters Parameters()const;
 const KartDynamics::State& GetState()const{return State;}
 static EKartGripSurface ClassifySurface(const FString& Names);
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart dynamics",meta=(ClampMin="80",ClampMax="300")) float MassKg=165;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart dynamics",meta=(ClampMin="25",ClampMax="200")) float YawInertiaKgM2=65;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart dynamics",meta=(ClampMin=".8",ClampMax="1.5")) float WheelbaseM=1.04f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart dynamics") float CGToFrontAxleM=.60f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart dynamics") float TrackWidthM=1.06f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart dynamics") float CGHeightM=.28f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart tires") float FrontCorneringStiffness=15000;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart tires") float RearCorneringStiffness=21000;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart tires") float RearGripScale=1.10f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart tires") float SlidingGripDrop=.12f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart tires") float RelaxationLengthM=.18f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart tires") float RearAxleScrub=8;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart power") float EngineForceN=710;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart power") float BrakeForceN=550;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart power",meta=(ClampMin="0",ClampMax="1")) float RearBrakeBias=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart power") float LinearDragPerSecond=.32f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart power") float RollingResistanceN=15;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart steering") float MaximumSteeringDegrees=24;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart steering") float SteeringRateRadPerSecond=3.2f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart steering") float HighSpeedSteeringReduction=.45f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart surfaces") float AsphaltGrip=1.05f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart surfaces") float CurbGrip=.85f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart surfaces") float GrassGrip=.48f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart surfaces") float DirtGrip=.42f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart slip detection") float DriftEnterDegrees=6;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart slip detection") float DriftExitDegrees=3;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart slip detection") float DriftMinimumSpeedMps=3;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart slip detection") float DriftSustainSeconds=.12f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart slip detection") float GripRecoverySeconds=.18f;
 /** Optional existing sound only. No audio is synthesized when unassigned. */
 UPROPERTY(EditAnywhere,Category="Kart feedback") TSoftObjectPtr<USoundBase> TireScrubSound;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart diagnostics") bool bLogTelemetry=false;
 UPROPERTY(BlueprintReadOnly,Category="Kart diagnostics") FKartSlipTelemetry Telemetry;
 UPROPERTY(BlueprintReadOnly,Category="Kart diagnostics") float DroppedSimulationSeconds=0;
 UPROPERTY(BlueprintReadOnly,Category="Kart diagnostics") int32 CollisionCount=0;
 UPROPERTY(BlueprintReadOnly,Category="Kart diagnostics") int32 StepCount=0;
private:
 KartDynamics::State State;
 KartDynamics::Contact Contact;
 double Accumulator=0,VerticalSpeed=0,LogClock=0,FlushClock=0;
 bool bHasGround=false;
 float GroundHeight=0;
 FString LogPath,LogRows;
 UPROPERTY(Transient) TObjectPtr<UAudioComponent> ScrubAudio;
 void ProbeGround();
 void Publish();
 void WriteLog(float Dt);
};
