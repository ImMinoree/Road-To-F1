#pragma once
#include "CoreMinimal.h"
namespace KartAwareness {
// Centimetres and seconds. The danger envelope includes both karts' collision boxes.
inline int32 Risk(FVector Local,FVector Velocity,double RouteGap){
 if(FMath::Abs(Local.Z)>200||Local.Size2D()>2500||(RouteGap>4500&&Local.Size2D()>350))return -1;
 if(FMath::Abs(Local.X)<230&&FMath::Abs(Local.Y)<220)return 2;
 const FVector2D P(Local),V(Velocity);
 const double T=V.SizeSquared()>1?-FVector2D::DotProduct(P,V)/V.SizeSquared():-1;
 if(T>0&&T<1.5){const auto Q=P+V*T;if(FMath::Abs(Q.X)<230&&FMath::Abs(Q.Y)<220)return T<.8?2:1;}
 return 0;
}
}
