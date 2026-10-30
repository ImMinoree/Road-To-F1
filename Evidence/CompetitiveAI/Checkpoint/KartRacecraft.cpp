#include "TrackRacingAI.h"
#include "KartRacecraftMath.h"
#include "ProofPawn.h"
#include "Engine/World.h"
#include "Algo/BinarySearch.h"

float UTrackRacingAI::PlanRacecraft(FTrackOpponent& S,const TArray<AProofPawn*>& Traffic,const TMap<AProofPawn*,float>& TrafficArcs,float Arc,float Speed,float Dt){
 auto* P=S.Pawn.Get();const FVector Position=P->GetActorLocation();const float Actual=Lateral(Position,S.Segment);const FVector Normal=FVector::CrossProduct(FVector::UpVector,Route->Tangent(S.Segment));
 const auto& Profile=S.Personality;const float Aggression=FMath::Clamp(Profile.Aggressiveness,0.f,1.f);
 auto Gap=[&](AProofPawn* Other){return KartRacecraft::SignedGap(TrafficArcs[Other],Arc,RouteLength);};
 auto Lane=[&](AProofPawn* Other){const int32 I=FMath::Clamp(Algo::UpperBound(Arcs,TrafficArcs[Other])-1,0,Route->Center.Num()-1);return Lateral(Other->GetActorLocation(),I);};
 auto Guide=[&](int32 I){return Route->Guide.Num()==Route->Center.Num()?Lateral(Route->Guide[I],I):0.f;};
 auto Safe=[&](float Candidate,bool Predict){
  for(float Ahead:{0.f,350.f,700.f,1200.f,1800.f}){const int32 I=AheadIndex(S.Segment,Ahead);if(FMath::Abs(Route->ClampLane(I,Candidate+Guide(I)-Guide(S.Segment),175)-(Candidate+Guide(I)-Guide(S.Segment)))>1)return false;}
  for(auto* Other:Traffic){if(Other==P)continue;const float D=Gap(Other);if(FMath::Abs(D)>2200||FVector::Dist2D(Position,Other->GetActorLocation())>2500)continue;
   if(Predict?KartRacecraft::Conflict(D,Other->GetDrivingSpeed(),Speed,Lane(Other),Candidate):(FMath::Abs(D)<310&&FMath::Abs(Lane(Other)-Candidate)<205))return false;
  }return true;
 };
 S.IntentAge+=Dt;S.RacecraftCooldown=FMath::Max(0.f,S.RacecraftCooldown-Dt);S.bAlongside=false;
 AProofPawn* Leader=nullptr;AProofPawn* Chaser=nullptr;float LeaderGap=2200,ChaserGap=-1400;
 for(auto* Other:Traffic){if(Other==P)continue;const float D=Gap(Other);if(FVector::Dist2D(Position,Other->GetActorLocation())>2500)continue;const float Side=Lane(Other)-Actual;
  if(FMath::Abs(D)<300&&FMath::Abs(Side)<650)S.bAlongside=true;
  if(D>0&&D<LeaderGap&&FMath::Abs(Side)<200){Leader=Other;LeaderGap=D;}
  if(D<-300&&D>ChaserGap&&FMath::Abs(Side)<500){Chaser=Other;ChaserGap=D;}
 }
 const int32 BendIndex=AheadIndex(S.Segment,1400);const float Bend=FMath::Atan2(FVector::CrossProduct(Route->Tangent(S.Segment),Route->Tangent(BendIndex)).Z,FVector::DotProduct(Route->Tangent(S.Segment),Route->Tangent(BendIndex)));
 // Once overlap starts, keep the lane. Never cross a rival's occupied lane to defend or merge.
 if(S.Intent==1||S.Intent==2){
  auto* Rival=S.Rival.Get();const float D=Rival?Gap(Rival):-1000;
  if(Rival&&D<-400&&!S.bAlongside){++S.PassesCompleted;S.Intent=0;S.RacecraftCooldown=2;S.IntentAge=0;S.Rival.Reset();}
  else if(!S.bAlongside&&((S.IntentAge>1.2f&&!Safe(S.DesiredLane,true))||S.IntentAge>18)){
   ++S.AbortedPasses;S.Intent=4;S.IntentAge=0;S.RacecraftCooldown=3;
  }
 }else if(S.Intent==3){
  if(S.IntentAge>3){if(Chaser&&!S.bAlongside)++S.DefensiveHolds;S.Intent=0;S.RacecraftCooldown=8;S.IntentAge=0;}
 }else if(S.Intent==4){
  const float Return=Route->ClampLane(S.Segment,Guide(S.Segment),175);
  if(!S.bAlongside&&Safe(Return,true)){S.DesiredLane=Return;if(FMath::Abs(Actual-Return)<55){S.Intent=0;S.IntentAge=0;}}
 }
 if(S.Intent==0&&!S.bAlongside){
  const float Preferred=Route->ClampLane(S.Segment,Guide(S.Segment)+Profile.PassingPreference*35,175);
  if(Safe(Preferred,true))S.DesiredLane=Preferred;
  if(Leader&&LeaderGap>400&&LeaderGap<1800&&S.RacecraftCooldown<=0&&(Leader->GetDrivingSpeed()<S.CruiseSpeed-30||LeaderGap<900)){
   const float OtherLane=Lane(Leader);float Best=0,BestScore=-MAX_flt;
   for(float Side:{-1.f,1.f}){const float Candidate=OtherLane+Side*250;
    if(!Safe(Candidate,true))continue;
    // Prefer inside before a bend; configured preference resolves similar gaps deterministically.
    const float Score=Side*Profile.PassingPreference*35+Side*FMath::Sign(Bend)*FMath::Abs(Bend)*60-FMath::Abs(Candidate-Actual)*.03f;
    if(Score>BestScore){BestScore=Score;Best=Candidate;}
   }
   if(BestScore>-MAX_flt){S.DesiredLane=Best;S.Intent=Best>Actual?1:2;S.IntentAge=0;S.Rival=Leader;++S.PassAttempts;}
  }
  if(S.Intent==0&&Chaser&&Aggression>.45f&&KartRacecraft::MayDefend(ChaserGap,S.bAlongside,S.RacecraftCooldown,Bend)){
   const float Inside=Route->ClampLane(S.Segment,Guide(S.Segment)+FMath::Sign(Bend)*85,175);
   if(Safe(Inside,true)){S.DesiredLane=Inside;S.Intent=3;S.IntentAge=0;}
  }
 }
 // Freeze any lateral transition during overlap if it would erase the occupied corridor.
 if(S.bAlongside&&!Safe(S.DesiredLane,false))S.DesiredLane=Actual;
 S.DesiredLane=Route->ClampLane(S.Segment,S.DesiredLane,175);
 S.Lane=FMath::FInterpConstantTo(S.Lane,S.DesiredLane,Dt,85+Aggression*40);
 float Limit=S.CruiseSpeed;
 for(auto* Other:Traffic){if(Other==P)continue;const float D=Gap(Other);if(D<=0||D>1800||FVector::Dist2D(Position,Other->GetActorLocation())>2500)continue;
  // Follow only while our actual or imminent trajectory overlaps the other kart's lane.
  const float Side=Lane(Other);if(FMath::Abs(Side-Actual)<190||FMath::Abs(Side-S.DesiredLane)<190){
   const float Clearance=310+(1-Aggression)*90;Limit=FMath::Min(Limit,FMath::Max(0.f,Other->GetDrivingSpeed()+(D-Clearance)*.65f));
  }
 }
 S.BlockedSeconds=Speed<30&&Leader&&LeaderGap<700&&FMath::Abs(Leader->GetDrivingSpeed())<30?S.BlockedSeconds+Dt:0;
 return Limit;
}
FString UTrackRacingAI::GetRacecraftTelemetry() const {
 FString Rows;for(const auto& S:Opponents){if(!Rows.IsEmpty())Rows+=TEXT(",");Rows+=FString::Printf(TEXT("{\"slot\":%d,\"intent\":%d,\"attempts\":%d,\"completed\":%d,\"aborted\":%d,\"defensive_holds\":%d,\"blocked_seconds\":%.3f,\"lane\":%.2f,\"desired\":%.2f}"),S.Slot,S.Intent,S.PassAttempts,S.PassesCompleted,S.AbortedPasses,S.DefensiveHolds,S.BlockedSeconds,S.Lane,S.DesiredLane);}
 return TEXT("[")+Rows+TEXT("]");
}
