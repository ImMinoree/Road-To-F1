#pragma once
#include "CoreMinimal.h"

// Rendering kinematics only, centimetres. X forward, Y right, Z up.
namespace KartVisual {
inline FVector ColumnAxis(){return FVector(.573576436,0,-.819152044);}
inline FVector WheelCenter(){return FVector(23,0,52);}
inline FVector ColumnBottom(){return WheelCenter()+ColumnAxis()*35;}
inline FVector Pin(float ColumnDegrees){
 return ColumnBottom()+FQuat(ColumnAxis(),FMath::DegreesToRadians(ColumnDegrees)).RotateVector(FVector(8,0,8/FMath::Tan(FMath::DegreesToRadians(55.f))));
}
inline FVector Kingpin(int Side){return FVector(60,Side*46,17.589);}
inline FVector Pickup(int Side,float Degrees){return Kingpin(Side)+FQuat(FVector::UpVector,FMath::DegreesToRadians(Degrees)).RotateVector(FVector(-11,-Side*4.9,0));}
inline float RodLength(int Side){return FVector::Dist(Pin(0),Pickup(Side,0));}
inline float Knuckle(int Side,float Column){
 // Newton solve the fixed rod / steering arm circle intersection on the continuous centre branch.
 float Angle=Column*.6f;
 for(int I=0;I<16;++I){
  auto Error=[&](float A){return FVector::Dist(Pin(Column),Pickup(Side,A))-RodLength(Side);};
  const float Derivative=(Error(Angle+.05f)-Error(Angle-.05f))/.1f;
  if(FMath::Abs(Derivative)<.0001f)break;
  Angle=FMath::Clamp(Angle-Error(Angle)/Derivative,-60.f,60.f);
 }
 return Angle;
}
struct Steering {float Column=0,Left=0,Right=0;};
// The authored cockpit column axis points away from the driver. Its visible
// wheel/hand rotation has the opposite sign to the linkage solver's input.
inline float SteeringWheelDegrees(float LinkageColumnDegrees){return -LinkageColumnDegrees;}
inline Steering Solve(float AuthoritativeDegrees){
 float Lo=-45,Hi=45;
 for(int I=0;I<18;++I){float Mid=(Lo+Hi)*.5f;float Mean=(Knuckle(-1,Mid)+Knuckle(1,Mid))*.5f;if(Mean<AuthoritativeDegrees)Lo=Mid;else Hi=Mid;}
 Steering S;S.Column=(Lo+Hi)*.5f;S.Left=Knuckle(-1,S.Column);S.Right=Knuckle(1,S.Column);return S;
}
}

