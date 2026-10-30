#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Components/ActorComponent.h"
#include "TrackRacingAI.generated.h"
class AProofPawn;
class USkeletalMeshComponent;
class UStaticMeshComponent;
USTRUCT(BlueprintType)
struct FKartDriverPersonality {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float Aggressiveness=.6f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float BrakingConfidence=.9f;
 /** -1 prefers right, +1 left; zero chooses the best available gap. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float PassingPreference=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float Consistency=.95f;
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
 FKartDriverPersonality Personality;
 TWeakObjectPtr<AProofPawn> Rival;
 int32 Intent=0,PassAttempts=0,PassesCompleted=0,AbortedPasses=0,DefensiveHolds=0,ReverseAttempts=0;
 float IntentAge=0,RacecraftCooldown=0,BlockedSeconds=0,RecoveryWindow=0;
 bool bAlongside=false;
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
 UPROPERTY(EditDefaultsOnly,Category="Racing AI",meta=(ClampMin="0",ClampMax="9")) int32 OpponentCount=4;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Racecraft") bool bEnableRacecraft=true;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Racecraft") TArray<FKartDriverPersonality> Drivers;
 UFUNCTION(BlueprintPure,Category="Racecraft") FString GetRacecraftTelemetry() const;
 UPROPERTY(EditDefaultsOnly,Category="Racing AI") TSoftObjectPtr<UTrackEdgeRoute> RouteAsset;
private:
 UPROPERTY() TObjectPtr<UTrackEdgeRoute> Route;
 TArray<FTrackOpponent> Opponents;
 FTrackOpponent TestPlayer;
 TArray<float> Arcs;
 float RouteLength=0,ReportClock=0,TestRaceSeconds=0;
 bool bTesting=false,bReported=false,bGateCaptured=false;
 int32 NearestSegment(const FVector& Position,int32 Previous) const;
 float SegmentArc(const FVector& Position,int32 Segment) const;
 float Lateral(const FVector& Position,int32 Segment) const;
 int32 AheadIndex(int32 Segment,float Distance) const;
 void CreatePresentation(FTrackOpponent& State);
 void WriteEvidence(bool bFinal);
 float PlanRacecraft(FTrackOpponent& State,const TArray<AProofPawn*>& Traffic,const TMap<AProofPawn*,float>& TrafficArcs,float Arc,float Speed,float Dt);
};
