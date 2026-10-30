#include "KartAITrackPlan.h"
#include "TrackRacingAI.h"
#include "KartTireDynamics.h"
#include "KartRaceSettings.h"
void FKartAITrackPlan::Build(const UTrackEdgeRoute* Route,const UKartTireDynamics* D,float CornerBudget,float ExitBudget){
 Samples.Reset();if(!Route||!Route->IsUsable()||!D)return;const int32 N=Route->Center.Num();Samples.SetNum(N);
 BrakeDeceleration=FMath::Min(D->BrakeForceN/D->MassKg*100.f*.70f,D->AsphaltGrip*981.f*.45f);
 LateralAcceleration=FMath::Min(FMath::Clamp(CornerBudget,200.f,500.f),D->AsphaltGrip*981.f*.55f);Acceleration=FMath::Clamp(ExitBudget,100.f,350.f);
 for(int32 I=0;I<N;++I){auto& S=Samples[I];S.Position=Route->LanePoint(I,0,175);const FVector Normal=FVector::CrossProduct(FVector::UpVector,Route->Tangent(I));S.Left=FVector::DotProduct(Route->Left[I]-Route->Center[I],Normal);S.Right=FVector::DotProduct(Route->Right[I]-Route->Center[I],Normal);S.Width=S.Left-S.Right;S.Grip=D->AsphaltGrip;}
 for(int32 I=0;I<N;++I){auto& S=Samples[I];const FVector A=Samples[(I+N-3)%N].Position,B=S.Position,C=Samples[(I+3)%N].Position;const FVector AB=B-A,BC=C-B,AC=C-A;
  S.Curvature=2.f*FVector::CrossProduct(AB,AC).Z/FMath::Max(1.f,float(AB.Size2D()*BC.Size2D()*AC.Size2D()));
  S.Grade=(C.Z-A.Z)/FMath::Max(1.f,float(AC.Size2D()));S.Speed=FMath::Min(D->MaximumForwardSpeedMph*44.704f,FMath::Sqrt(LateralAcceleration/FMath::Max(.00001f,FMath::Abs(S.Curvature))));
 }
 // Cache the corner/braking ceiling separately from the conservative exit ramp.
 // On a settled clear straight the controller may demand full available motor torque.
 for(int32 Pass=0;Pass<4;++Pass)for(int32 I=N-1;I>=0;--I){const int32 J=(I+1)%N;const float Ds=FVector::Dist2D(Samples[I].Position,Samples[J].Position);const float Decel=FMath::Max(100.f,BrakeDeceleration+981.f*Samples[I].Grade);Samples[I].Speed=FMath::Min(Samples[I].Speed,FMath::Sqrt(FMath::Square(Samples[J].Speed)+2*Decel*Ds));}
 for(auto& Sample:Samples)Sample.BrakingSpeed=Sample.Speed;
 // Cyclic backward braking pass, followed by physically bounded exit acceleration.
 for(int32 Pass=0;Pass<4;++Pass){for(int32 I=N-1;I>=0;--I){const int32 J=(I+1)%N;const float Ds=FVector::Dist2D(Samples[I].Position,Samples[J].Position);const float Decel=FMath::Max(100.f,BrakeDeceleration+981.f*Samples[I].Grade);Samples[I].Speed=FMath::Min(Samples[I].Speed,FMath::Sqrt(FMath::Square(Samples[J].Speed)+2*Decel*Ds));}
  for(int32 I=0;I<N;++I){const int32 J=(I+1)%N;const float Ds=FVector::Dist2D(Samples[I].Position,Samples[J].Position);Samples[J].Speed=FMath::Min(Samples[J].Speed,FMath::Sqrt(FMath::Square(Samples[I].Speed)+2*Acceleration*Ds));}
 }
 for(int32 I=0;I<N;++I){auto& S=Samples[I];float Distance=0;S.BendDistance=10000;for(int32 K=1;K<100;++K){const int32 J=(I+K)%N;Distance+=FVector::Dist2D(Samples[(J+N-1)%N].Position,Samples[J].Position);if(FMath::Abs(Samples[J].Curvature)>.001f){S.BendDistance=Distance;break;}}
  const float Before=FMath::Abs(Samples[(I+N-5)%N].Curvature),After=FMath::Abs(Samples[(I+5)%N].Curvature),Here=FMath::Abs(S.Curvature);S.Zone=Here<.0003f?0:After>Here*1.1f?1:Before>Here*1.1f?3:2;
 }
}
