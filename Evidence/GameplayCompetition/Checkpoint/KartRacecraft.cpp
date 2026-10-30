#include "TrackRacingAI.h"
#include "KartRacecraftMath.h"
#include "ProofPawn.h"
#include "KartTireDynamics.h"
#include "Engine/World.h"
#include "Algo/BinarySearch.h"

float UTrackRacingAI::PlanRacecraft(FTrackOpponent& S,const TArray<AProofPawn*>& Traffic,const TMap<AProofPawn*,float>& TrafficArcs,float Arc,float Speed,float Dt){
 auto* P=S.Pawn.Get();const FVector Position=P->GetActorLocation();const float Actual=Lateral(Position,S.Segment);const FVector Normal=FVector::CrossProduct(FVector::UpVector,Route->Tangent(S.Segment));
 const auto& Profile=S.Personality;const float Aggression=FMath::Clamp(Profile.Aggressiveness,0.f,1.f);
 auto Gap=[&](AProofPawn* Other){return KartRacecraft::SignedGap(TrafficArcs[Other],Arc,RouteLength);};
 auto Lane=[&](AProofPawn* Other){const int32 I=FMath::Clamp(Algo::UpperBound(Arcs,TrafficArcs[Other])-1,0,Route->Center.Num()-1);return Lateral(Other->GetActorLocation(),I);};
 auto Guide=[&](int32 I){return Route->Guide.Num()==Route->Center.Num()?Lateral(Route->Guide[I],I):0.f;};
 auto Feasible=[&](float Candidate){
  for(float Ahead:{0.f,350.f,700.f,1200.f,1800.f}){const int32 I=AheadIndex(S.Segment,Ahead);if(TrackPlan.Samples.IsValidIndex(I)){const float K=TrackPlan.Samples[I].Curvature;const auto* D=P->GetTireDynamics();const float MinimumRadius=D?D->WheelbaseM*100/FMath::Tan(FMath::DegreesToRadians(D->MaximumSteeringDegrees))*1.1f:260;if(FMath::Abs(K)>.0001f&&FMath::Sign(K)*(Candidate-Guide(S.Segment))>FMath::Max(0.f,1/FMath::Abs(K)-MinimumRadius))return false;}if(FMath::Abs(Route->ClampLane(I,Candidate+Guide(I)-Guide(S.Segment),175)-(Candidate+Guide(I)-Guide(S.Segment)))>1)return false;}
  return true;
 };
 auto Safe=[&](float Candidate,bool Predict){if(!Feasible(Candidate))return false;
  for(auto* Other:Traffic){if(Other==P)continue;const float D=Gap(Other);if(FMath::Abs(D)>2200||FVector::Dist2D(Position,Other->GetActorLocation())>2500)continue;
   float LateralVelocity=0,HalfWidth=60;for(const auto& O:S.Nearby)if(O.Pawn.Get()==Other){LateralVelocity=O.LateralVelocity;HalfWidth=O.HalfWidth;break;}
   const float Room=FMath::Max(205.f,HalfWidth+90*FMath::Abs(FVector::DotProduct(P->GetActorForwardVector(),Normal))+60*FMath::Abs(FVector::DotProduct(P->GetActorRightVector(),Normal))+MinimumRacingRoomCm);
   if(Predict){for(float T:{0.f,.5f,1.f,1.5f})if(FMath::Abs(D+(Other->GetDrivingSpeed()-Speed)*T)<270&&FMath::Abs(Lane(Other)+LateralVelocity*T-Candidate)<Room)return false;}
   else if(FMath::Abs(D)<310&&FMath::Abs(Lane(Other)-Candidate)<Room)return false;
  }return true;
 };
 S.IntentAge+=Dt;S.RacecraftCooldown=FMath::Max(0.f,S.RacecraftCooldown-Dt);S.bAlongside=false;
 AProofPawn* Leader=nullptr;AProofPawn* Chaser=nullptr;float LeaderGap=2200,ChaserGap=-1400;
 for(auto* Other:Traffic){if(Other==P)continue;const float D=Gap(Other);if(FVector::Dist2D(Position,Other->GetActorLocation())>2500)continue;const float Side=Lane(Other)-Actual;
  if(FMath::Abs(D)<300&&FMath::Abs(Side)<350)S.bAlongside=true;
  if(D>0&&D<LeaderGap&&FMath::Abs(Side)<200){Leader=Other;LeaderGap=D;}
  if(D<-300&&D>ChaserGap&&FMath::Abs(Side)<500){Chaser=Other;ChaserGap=D;}
 }
 if(S.PerceivedLeader.IsValid()){auto* Kept=S.PerceivedLeader.Get();const float D=Gap(Kept);if(D>0&&D<LeaderGap+200&&FMath::Abs(Lane(Kept)-Actual)<210){Leader=Kept;LeaderGap=D;}}
 S.NearestGap=LeaderGap;S.MinimumTTC=1000;for(const auto& O:S.Nearby)S.MinimumTTC=FMath::Min(S.MinimumTTC,O.TTC);
 const int32 BendIndex=AheadIndex(S.Segment,1400);const float Bend=FMath::Atan2(FVector::CrossProduct(Route->Tangent(S.Segment),Route->Tangent(BendIndex)).Z,FVector::DotProduct(Route->Tangent(S.Segment),Route->Tangent(BendIndex)));
 // Once overlap starts, keep the lane. Never cross a rival's occupied lane to defend or merge.
 if(S.Intent!=4&&!Feasible(S.DesiredLane)){if(S.Intent==1||S.Intent==2||S.Intent==5)++S.AbortedPasses;S.Intent=4;S.IntentAge=0;S.RacecraftCooldown=3;}
 if(S.Intent==5){
  auto* Rival=S.Rival.Get();if(!Rival||!Safe(S.ProposedLane,true)||Gap(Rival)<250){S.Intent=4;S.IntentAge=0;S.RacecraftCooldown=2;++S.AbortedPasses;}
  else if(S.IntentAge>=PreparationDelay+Profile.ReactionDelay){S.DesiredLane=S.ProposedLane;S.Intent=S.ProposedLane>Actual?1:2;S.IntentAge=0;++S.PassAttempts;}
 }else if(S.Intent==1||S.Intent==2){
  auto* Rival=S.Rival.Get();const float D=Rival?Gap(Rival):-1000;
  if(Rival&&D<-400&&!S.bAlongside){++S.PassesCompleted;S.Intent=0;S.RacecraftCooldown=2;S.IntentAge=0;S.Rival.Reset();}
  else if(!S.bAlongside&&(!Rival||(S.IntentAge>1.2f&&!Safe(S.DesiredLane,true))||S.IntentAge>18)){
   ++S.AbortedPasses;S.Intent=4;S.IntentAge=0;S.RacecraftCooldown=3;
  }
 }else if(S.Intent==3){
  if(S.IntentAge>3){if(Chaser&&!S.bAlongside)++S.DefensiveHolds;S.Intent=0;S.RacecraftCooldown=8;S.IntentAge=0;}
 }else if(S.Intent==4){
  const float Return=Route->ClampLane(S.Segment,Guide(S.Segment),175);
  if(Safe(Return,true)){S.DesiredLane=Return;if(FMath::Abs(Actual-Return)<55){S.Intent=0;S.IntentAge=0;}}
 }
 if(S.Intent==0&&!S.bAlongside){
  const float Preferred=Route->ClampLane(S.Segment,Guide(S.Segment)+Profile.PassingPreference*35,175);
  if(Safe(Preferred,true))S.DesiredLane=Preferred;else if(Safe(Guide(S.Segment),true))S.DesiredLane=Guide(S.Segment);
  const auto* Dynamics=P->GetTireDynamics();const float Braking=Dynamics?Dynamics->BrakeForceN/Dynamics->MassKg*70.f:200.f;
  const float RequiredDistance=Leader?FMath::Max(0.f,(Speed*Speed-FMath::Square(Leader->GetDrivingSpeed()))/(2*FMath::Max(100.f,Braking))):0;
  if(Leader&&LeaderGap>400&&LeaderGap<1400+400*FMath::Clamp(Profile.OvertakingWillingness,0.f,1.f)&&RequiredDistance<LeaderGap+150&&S.RacecraftCooldown<=0&&(Leader->GetDrivingSpeed()<S.CruiseSpeed-30||LeaderGap<900)){
   const float OtherLane=Lane(Leader);float Best=0,BestScore=-MAX_flt;
   for(float Side:{-1.f,1.f}){const float Candidate=OtherLane+Side*250;
    if(!Safe(Candidate,true))continue;
    // Prefer inside before a bend; configured preference resolves similar gaps deterministically.
    const float Score=Side*Profile.PassingPreference*35+Side*FMath::Sign(Bend)*FMath::Abs(Bend)*60-FMath::Abs(Candidate-Actual)*.03f;
    if(Score>BestScore){BestScore=Score;Best=Candidate;}
   }
   if(BestScore>-MAX_flt){S.ProposedLane=Best;S.Intent=5;S.IntentAge=0;S.Rival=Leader;}
  }
  if(S.Intent==0&&Chaser&&Profile.DefensiveTendency>.35f&&Aggression>.45f&&KartRacecraft::MayDefend(ChaserGap,S.bAlongside,S.RacecraftCooldown,Bend)){
   const float Inside=Route->ClampLane(S.Segment,Guide(S.Segment)+FMath::Sign(Bend)*85,175);
   if(Safe(Inside,true)){S.DesiredLane=Inside;S.Intent=3;S.IntentAge=0;}
  }
 }
 // Freeze any lateral transition during overlap if it would erase the occupied corridor.
 if(S.bAlongside&&!Safe(S.DesiredLane,false))S.DesiredLane=Actual;
 S.DesiredLane=Route->ClampLane(S.Segment,S.DesiredLane,175);

 float Limit=S.CruiseSpeed;
 for(auto* Other:Traffic){if(Other==P)continue;const float D=Gap(Other);if(D<=0||D>1800||FVector::Dist2D(Position,Other->GetActorLocation())>2500)continue;
  // Follow only while our actual or imminent trajectory overlaps the other kart's lane.
  const float Side=Lane(Other);if(FMath::Abs(Side-Actual)<190||FMath::Abs(Side-S.DesiredLane)<190){
   const float Clearance=310+(1-Aggression)*90;Limit=FMath::Min(Limit,FMath::Max(0.f,Other->GetDrivingSpeed()+(D-Clearance)*.65f));
  }
 }
 S.BlockedSeconds=Speed<30&&Leader&&LeaderGap<700&&FMath::Abs(Leader->GetDrivingSpeed())<30?S.BlockedSeconds+Dt:0;
 EKartAIState Next=Leader?(LeaderGap>1100?EKartAIState::CATCH_OPPONENT:EKartAIState::FOLLOW_OPPONENT):EKartAIState::FOLLOW_RACING_LINE;
 if(S.Intent==5)Next=EKartAIState::PREPARE_OVERTAKE;
 if(S.Intent==1||S.Intent==2)Next=(S.DesiredLane-Guide(S.Segment))*Bend>=0?EKartAIState::OVERTAKE_INSIDE:EKartAIState::OVERTAKE_OUTSIDE;
 if(S.Intent==3)Next=EKartAIState::DEFEND_POSITION;if(S.Intent==4)Next=EKartAIState::YIELD_OR_ABORT;if(S.bAlongside)Next=EKartAIState::SIDE_BY_SIDE;
 if(S.State!=Next){S.State=Next;++S.StateEntries[int32(Next)];}
 if(!Feasible(S.DesiredLane)){Limit=0;S.State=EKartAIState::YIELD_OR_ABORT;}
 return Limit;
}
FString UTrackRacingAI::GetRacecraftTelemetry() const {
 TArray<const FTrackOpponent*> States;for(const auto& S:Opponents)States.Add(&S);if(TestPlayer.Pawn.IsValid())States.Add(&TestPlayer);FString Rows;for(const auto* Ptr:States){const auto& S=*Ptr;if(!Rows.IsEmpty())Rows+=TEXT(",");Rows+=FString::Printf(TEXT("{\"slot\":%d,\"intent\":%d,\"attempts\":%d,\"completed\":%d,\"aborted\":%d,\"defensive_holds\":%d,\"blocked_seconds\":%.3f,\"lane\":%.2f,\"desired\":%.2f}"),S.Slot,S.Intent,S.PassAttempts,S.PassesCompleted,S.AbortedPasses,S.DefensiveHolds,S.BlockedSeconds,S.Lane,S.DesiredLane);
  Rows.RemoveFromEnd(TEXT("}"));Rows+=FString::Printf(TEXT(",\"id\":\"%s\",\"state\":\"%s\",\"speed_cms\":%.2f,\"target_cms\":%.2f,\"throttle\":%.3f,\"brake\":%.3f,\"steering\":%.3f,\"line_error_cm\":%.2f,\"grip\":%.3f,\"nearest_gap_cm\":%.2f,\"ttc\":%.3f,\"state_entries\":["),S.Pawn.IsValid()?*S.Pawn->GetName():TEXT("none"),*StaticEnum<EKartAIState>()->GetNameStringByValue(int64(S.State)),S.Pawn.IsValid()?S.Pawn->GetDrivingSpeed():0,S.DebugTargetSpeed,S.ThrottleCommand,S.BrakeCommand,S.Steering,S.LineError,S.GripEstimate,S.NearestGap,S.MinimumTTC);for(int32 I=0;I<10;++I){if(I)Rows+=TEXT(",");Rows+=FString::FromInt(S.StateEntries[I]);}Rows+=TEXT("]}");
  FString Observations;for(const auto& O:S.Nearby){if(!Observations.IsEmpty())Observations+=TEXT(",");Observations+=FString::Printf(TEXT("{\"id\":\"%s\",\"gap\":%.2f,\"lane\":%.2f,\"relative_speed\":%.2f,\"ttc\":%.3f,\"alongside\":%s}"),O.Pawn.IsValid()?*O.Pawn->GetName():TEXT("none"),O.Gap,O.Lane,O.RelativeSpeed,O.TTC,O.Alongside?TEXT("true"):TEXT("false"));}Rows.RemoveFromEnd(TEXT("}"));Rows+=TEXT(",\"perception\":[")+Observations+FString::Printf(TEXT("],\"mistakes\":%d,\"laps\":%d,\"recoveries\":%d}"),S.Mistakes,S.Laps,S.Recoveries);}
 return TEXT("[")+Rows+TEXT("]");
}
