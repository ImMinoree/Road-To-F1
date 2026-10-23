#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerStart.h"
#include "GridStartSlot.generated.h"
// A real configurable spawn actor, independent of decorative road markings.
UCLASS()
class ROAD_TO_F1_NEW_API AGridStartSlot : public APlayerStart {
 GENERATED_BODY()
public:
 AGridStartSlot(const FObjectInitializer& ObjectInitializer=FObjectInitializer::Get());
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart grid",meta=(ClampMin="1",ClampMax="20")) int32 PositionNumber=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Kart grid") FVector KartSafetyHalfExtents=FVector(110,90,77.5);
};

