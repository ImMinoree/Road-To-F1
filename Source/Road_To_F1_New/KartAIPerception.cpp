#include "TrackRacingAI.h"
#include "ProofPawn.h"
#include "KartRacecraftMath.h"
#include "Components/BoxComponent.h"
#include "Algo/BinarySearch.h"
void UTrackRacingAI::ObserveOpponents(FTrackOpponent& S,const TArray<AProofPawn*>& Traffic,const TMap<AProofPawn*,float>& TrafficArcs,float Dt){
 S.Nearby.Reset();auto* Own=S.Pawn.Get();if(!Own||!TrafficArcs.Contains(Own))return;const float Arc=TrafficArcs[Own];const FVector Pos=Own->GetActorLocation();float Best=3500;AProofPawn* Candidate=nullptr;
 for(auto* P:Traffic){if(P==Own||FVector::DistSquared2D(Pos,P->GetActorLocation())>3600.f*3600)continue;
  const float Gap=KartRacecraft::SignedGap(TrafficArcs[P],Arc,RouteLength);if(FMath::Abs(Gap)>3500)continue;const int32 I=FMath::Clamp(Algo::UpperBound(Arcs,TrafficArcs[P])-1,0,Route->Center.Num()-1);
  FTrackOpponent::FObservation O;O.Pawn=P;O.Gap=Gap;O.Lane=Lateral(P->GetActorLocation(),I);O.RelativeSpeed=P->GetDrivingSpeed()-Own->GetDrivingSpeed();O.Predicted=P->GetActorLocation()+P->GetVelocity()*.75;
  const FVector Tangent=Route->Tangent(I),Normal=FVector::CrossProduct(FVector::UpVector,Tangent);O.LateralVelocity=FMath::Clamp(float(FVector::DotProduct(P->GetVelocity(),Normal)),-250.f,250.f);
  if(const auto* Box=Cast<UBoxComponent>(P->GetRootComponent())){const FVector E=Box->GetScaledBoxExtent(),F=P->GetActorForwardVector(),R=P->GetActorRightVector();O.HalfLength=FMath::Abs(FVector::DotProduct(F,Tangent))*E.X+FMath::Abs(FVector::DotProduct(R,Tangent))*E.Y;O.HalfWidth=FMath::Abs(FVector::DotProduct(F,Normal))*E.X+FMath::Abs(FVector::DotProduct(R,Normal))*E.Y;}
  O.Alongside=FMath::Abs(Gap)<O.HalfLength+165&&FMath::Abs(O.Lane-S.Lane)<O.HalfWidth+500;
  if(Gap>0&&O.RelativeSpeed<-1)O.TTC=FMath::Max(0.f,Gap-O.HalfLength-90)/(-O.RelativeSpeed);
  if(Gap>0&&Gap<Best&&FMath::Abs(O.Lane-S.Lane)<210){Best=Gap;Candidate=P;}
  S.Nearby.Add(O);
 }
 S.PerceptionHold=FMath::Max(0.f,S.PerceptionHold-Dt);
 bool Keep=false;for(const auto& O:S.Nearby)if(O.Pawn==S.PerceivedLeader&&O.Gap>0&&O.Gap<2500&&FMath::Abs(O.Lane-S.Lane)<250)Keep=true;
 if(!Keep||S.PerceptionHold<=0){S.PerceivedLeader=Candidate;S.PerceptionHold=.5f;}
}
