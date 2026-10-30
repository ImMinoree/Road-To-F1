#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Components/ActorComponent.h"
#include "KartAITrackPlan.h"
#include "TrackRacingAI.generated.h"
class AProofPawn;
class USkeletalMeshComponent;
class UStaticMeshComponent;
UENUM(BlueprintType)
enum class EKartAIState:uint8 {FOLLOW_RACING_LINE,CATCH_OPPONENT,FOLLOW_OPPONENT,PREPARE_OVERTAKE,OVERTAKE_INSIDE,OVERTAKE_OUTSIDE,DEFEND_POSITION,SIDE_BY_SIDE,YIELD_OR_ABORT,RECOVER_TO_TRACK};
UENUM(BlueprintType)
enum class EKartAIDifficulty:uint8 {ROOKIE,AMATEUR,INTERMEDIATE,PRO,ELITE};
struct FKartDifficultySettings {float LateralScale=1,BrakeMargin=.3f,Reaction=.2f,Smoothness=.5f,MistakeScale=1;};
USTRUCT(BlueprintType)
struct FKartDriverPersonality {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float Aggressiveness=.6f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float BrakingConfidence=.9f;
 /** Negative prefers left, positive right in the track frame. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float PassingPreference=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float Consistency=.95f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,meta=(ClampMin="0.65",ClampMax="1")) float Pace=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,meta=(ClampMin="0",ClampMax="1")) float SteeringSmoothness=.5f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,meta=(ClampMin="0",ClampMax="1")) float OvertakingWillingness=.85f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,meta=(ClampMin="0",ClampMax="1")) float DefensiveTendency=.7f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,meta=(ClampMin="0",ClampMax="0.3")) float ReactionDelay=.02f;
 /** Recoverable hesitation/poor-exit probability per eligible second, not random steering. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,meta=(ClampMin="0",ClampMax="0.05")) float MistakeLikelihood=.004f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,meta=(ClampMin="0.3",ClampMax="1")) float RecoverySkill=.85f;
};

/** Actual paired asphalt polygon edges, in the existing map's world centimeters. */
UCLASS(BlueprintType)
class ROAD_TO_F1_NEW_API UTrackEdgeRoute : public UDataAsset {
 GENERATED_BODY()
public:
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TArray<FVector> Center;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TArray<FVector> Left;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TArray<FVector> Right;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TArray<FVector> Guide;
 bool IsUsable() const;
 FVector Tangent(int32 Index) const;
 FVector LanePoint(int32 Index,float Lane,float Margin=140.f) const;
 float ClampLane(int32 Index,float Lane,float Margin=140.f) const;
};

struct FTrackOpponent {
 TWeakObjectPtr<AProofPawn> Pawn;
 TWeakObjectPtr<USkeletalMeshComponent> Driver;
 TWeakObjectPtr<UStaticMeshComponent> Wheel;
 int32 Segment=INDEX_NONE,Slot=0,Laps=0,Recoveries=0,OffTrackFrames=0,VisitedCount=0;
 TSet<int32> Visited;
 FVector GridPosition=FVector::ZeroVector,Previous=FVector::ZeroVector;
 float StartArc=0,PreviousArc=0,Distance=0,Lane=0,DesiredLane=0,Preference=0;
 float Steering=0,CruiseSpeed=1000,DecisionTime=0,StuckTime=0,ReverseTime=0,Cooldown=0;
 float MaximumEdgeExcess=0,MaximumGridMovement=0,MaximumSpeed=0;
 float DebugTargetSpeed=0;
 float ThrottleCommand=0,BrakeCommand=0,LineError=0,GripEstimate=1,SteeringCommand=0;
 FKartDriverPersonality Personality;
 TWeakObjectPtr<AProofPawn> Rival;
 int32 Intent=0,PassAttempts=0,PassesCompleted=0,AbortedPasses=0,DefensiveHolds=0,ReverseAttempts=0;
 float IntentAge=0,RacecraftCooldown=0,BlockedSeconds=0,RecoveryWindow=0;
 bool bAlongside=false;
 EKartAIState State=EKartAIState::FOLLOW_RACING_LINE;
 int32 StateEntries[10]={};float ProposedLane=0,NearestGap=10000,MinimumTTC=1000;
 struct FObservation {TWeakObjectPtr<AProofPawn> Pawn;float Gap=0,Lane=0,LateralVelocity=0,RelativeSpeed=0,TTC=1000,HalfLength=90,HalfWidth=60;bool Alongside=false;FVector Predicted=FVector::ZeroVector;};
 TArray<FObservation> Nearby;
 TWeakObjectPtr<AProofPawn> PerceivedLeader;
 float PerceptionHold=0;
 float StrategyClock=1,CachedTrafficLimit=2000,MistakeTimer=0,MistakeCooldown=20,LastLapSeconds=0;
 int32 Mistakes=0;FRandomStream Random;TArray<float> LapTimes;
};

/** Edge-aware opponents with bounded racecraft; inputs feed the shared kart pawn. */
UCLASS()
class ROAD_TO_F1_NEW_API UTrackRacingAI : public UActorComponent {
 GENERATED_BODY()
public:
 UTrackRacingAI();
 void InitializeOpponents();
 void ResetRace();
 virtual void TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* ThisTickFunction) override;
 UPROPERTY(EditDefaultsOnly,Category="Racing AI",meta=(ClampMin="0",ClampMax="19")) int32 OpponentCount=4;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Racing AI") EKartAIDifficulty Difficulty=EKartAIDifficulty::INTERMEDIATE;
 UFUNCTION(BlueprintCallable,Category="Racing AI") void SetDifficulty(EKartAIDifficulty Value);
 static FKartDifficultySettings Preset(EKartAIDifficulty Value);
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Racing AI debug") bool bDebugAI=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Racing AI debug") bool bDrawAIPaths=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Racecraft") bool bEnableRacecraft=true;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Racecraft",meta=(ClampMin="50",ClampMax="150")) float MinimumRacingRoomCm=70;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Racecraft",meta=(ClampMin="0.1",ClampMax="0.8")) float PreparationDelay=.2f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Racing AI") bool bUseAdvancedPlanner=true;
 UFUNCTION(BlueprintPure,Category="Racing AI") FString GetTrackPlanTelemetry() const;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Racecraft") TArray<FKartDriverPersonality> Drivers;
 UFUNCTION(BlueprintPure,Category="Racecraft") FString GetRacecraftTelemetry() const;
 UPROPERTY(EditDefaultsOnly,Category="Racing AI") TSoftObjectPtr<UTrackEdgeRoute> RouteAsset;
private:
 UPROPERTY() TObjectPtr<UTrackEdgeRoute> Route;
 TArray<FTrackOpponent> Opponents;
 FTrackOpponent TestPlayer;
 TArray<float> Arcs;
 FKartAITrackPlan TrackPlan;
 float RouteLength=0,ReportClock=0,TestRaceSeconds=0;
 float SenseClock=0;
 float TrafficRefreshClock=1;TArray<TWeakObjectPtr<AProofPawn>> CachedTraffic;
 int32 LastConsoleDifficulty=-2,CpuSamples=0;double CpuTotalMs=0,CpuMaxMs=0;float DebugClock=0;
 bool bTesting=false,bReported=false,bGateCaptured=false;
 int32 NearestSegment(const FVector& Position,int32 Previous) const;
 float SegmentArc(const FVector& Position,int32 Segment) const;
 float Lateral(const FVector& Position,int32 Segment) const;
 int32 AheadIndex(int32 Segment,float Distance) const;
 void CreatePresentation(FTrackOpponent& State);
 void WriteEvidence(bool bFinal);
 float PlanRacecraft(FTrackOpponent& State,const TArray<AProofPawn*>& Traffic,const TMap<AProofPawn*,float>& TrafficArcs,float Arc,float Speed,float Dt);
 void ObserveOpponents(FTrackOpponent& State,const TArray<AProofPawn*>& Traffic,const TMap<AProofPawn*,float>& TrafficArcs,float Dt);
 int32 ConfiguredOpponentCount()const;
 void ApplyConsoleConfiguration();
 float DriverPace(FTrackOpponent& State,float Dt);
 void DrawAIDiagnostics(float Dt);
};
