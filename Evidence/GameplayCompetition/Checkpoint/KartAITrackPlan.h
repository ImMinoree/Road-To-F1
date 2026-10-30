#pragma once
#include "CoreMinimal.h"
class UTrackEdgeRoute;class UKartTireDynamics;
struct FKartTrackSample {
 FVector Position=FVector::ZeroVector;
 float Curvature=0,Width=0,Grade=0,Speed=0,BendDistance=0,Grip=1,Left=0,Right=0;
 int32 Zone=0; // straight, entry, apex, exit
};
struct FKartAITrackPlan {
 TArray<FKartTrackSample> Samples;
 float BrakeDeceleration=200,LateralAcceleration=260,Acceleration=150;
 void Build(const UTrackEdgeRoute* Route,const UKartTireDynamics* Dynamics);
};
