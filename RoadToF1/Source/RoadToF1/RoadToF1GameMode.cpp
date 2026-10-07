// Copyright Epic Games, Inc. All Rights Reserved.

#include "RoadToF1GameMode.h"
#include "RoadToF1PlayerController.h"

ARoadToF1GameMode::ARoadToF1GameMode()
{
	PlayerControllerClass = ARoadToF1PlayerController::StaticClass();
}
