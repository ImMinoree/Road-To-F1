// Copyright Epic Games, Inc. All Rights Reserved.

#include "RoadToF1WheelFront.h"
#include "UObject/ConstructorHelpers.h"

URoadToF1WheelFront::URoadToF1WheelFront()
{
	AxleType = EAxleType::Front;
	bAffectedBySteering = true;
	MaxSteerAngle = 40.f;
}