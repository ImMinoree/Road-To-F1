#pragma once
#include "CoreMinimal.h"

// Pure projection/clipping/route math. World +X is north; +Y is east.
namespace KartNavigation {
struct FView {
 FVector2D WorldCenter=FVector2D::ZeroVector,PixelOrigin=FVector2D::ZeroVector;
 FBox2D Pixels=FBox2D(ForceInit);double YawDegrees=0,PixelsPerCm=1;
 FVector2D Project(const FVector2D& P)const {
  const double A=FMath::DegreesToRadians(YawDegrees);const FVector2D D=P-WorldCenter;
  return PixelOrigin+FVector2D(-FMath::Sin(A)*D.X+FMath::Cos(A)*D.Y,-FMath::Cos(A)*D.X-FMath::Sin(A)*D.Y)*PixelsPerCm;
 }
 FVector2D Unproject(const FVector2D& P)const {
  const double A=FMath::DegreesToRadians(YawDegrees);const FVector2D D=(P-PixelOrigin)/PixelsPerCm;
  return WorldCenter+FVector2D(-FMath::Sin(A)*D.X-FMath::Cos(A)*D.Y,FMath::Cos(A)*D.X-FMath::Sin(A)*D.Y);
 }
};
inline bool ClipLine(FVector2D& A,FVector2D& B,const FBox2D& R){
 const FVector2D D=B-A;double Lo=0,Hi=1;
 auto Edge=[&](double P,double Q){if(FMath::Abs(P)<1.e-9)return Q>=0;const double T=Q/P;if(P<0)Lo=FMath::Max(Lo,T);else Hi=FMath::Min(Hi,T);return Lo<=Hi;};
 if(!Edge(-D.X,A.X-R.Min.X)||!Edge(D.X,R.Max.X-A.X)||!Edge(-D.Y,A.Y-R.Min.Y)||!Edge(D.Y,R.Max.Y-A.Y))return false;
 B=A+D*Hi;A+=D*Lo;return true;
}
inline TArray<FVector2D> ClipPolygon(TArray<FVector2D> P,const FBox2D& R){
 for(int Edge=0;Edge<4 && P.Num();++Edge){
  TArray<FVector2D> Out;auto Distance=[&](FVector2D V){switch(Edge){case 0:return V.X-R.Min.X;case 1:return R.Max.X-V.X;case 2:return V.Y-R.Min.Y;default:return R.Max.Y-V.Y;}};
  FVector2D A=P.Last();double DA=Distance(A);
  for(const FVector2D B:P){const double DB=Distance(B);if((DA>=0)!=(DB>=0))Out.Add(A+(B-A)*(DA/(DA-DB)));if(DB>=0)Out.Add(B);A=B;DA=DB;}
  P=MoveTemp(Out);
 }
 return P;
}
struct FRoutePoint {int32 Segment=INDEX_NONE;double Fraction=0;FVector2D Position=FVector2D::ZeroVector;};
inline FRoutePoint Nearest(const TArray<FVector>& Route,FVector2D P){
 FRoutePoint Best;double Distance=TNumericLimits<double>::Max();
 for(int32 I=0;I<Route.Num();++I){const FVector2D A(Route[I]),D=FVector2D(Route[(I+1)%Route.Num()])-A;const double T=FMath::Clamp(FVector2D::DotProduct(P-A,D)/FMath::Max(D.SizeSquared(),1.e-9),0.,1.);const FVector2D Q=A+D*T;const double D2=(P-Q).SizeSquared();if(D2<Distance){Distance=D2;Best={I,T,Q};}}
 return Best;
}
inline double ForwardDistance(const TArray<FVector>& Route,const FRoutePoint& A,const FRoutePoint& B){
 if(A.Segment==INDEX_NONE||B.Segment==INDEX_NONE||Route.Num()<2)return 0;
 double Total=0,ArcA=0,ArcB=0;
 for(int32 I=0;I<Route.Num();++I){const double Len=FVector::Dist2D(Route[I],Route[(I+1)%Route.Num()]);if(I==A.Segment)ArcA=Total+A.Fraction*Len;if(I==B.Segment)ArcB=Total+B.Fraction*Len;Total+=Len;}
 return Total>0?FMath::Fmod(ArcB-ArcA+Total,Total):0;
}
}
