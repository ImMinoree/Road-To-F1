// Copyright Epic Games, Inc. All Rights Reserved.

#include "RoadToF1WheelRear.h"
#include "UObject/ConstructorHelpers.h"

URoadToF1WheelRear::URoadToF1WheelRear()
{
	AxleType = EAxleType::Rear;
	bAffectedByHandbrake = true;
	bAffectedByEngine = true;
}