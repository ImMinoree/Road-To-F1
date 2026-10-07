// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "RoadToF1Pawn.h"
#include "RoadToF1SportsCar.generated.h"

/**
 *  Sports car wheeled vehicle implementation
 */
UCLASS(abstract)
class ARoadToF1SportsCar : public ARoadToF1Pawn
{
	GENERATED_BODY()
	
public:

	ARoadToF1SportsCar();
};
