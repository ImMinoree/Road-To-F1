#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RaceTrackGate.generated.h"

/** Ordered, direction-aware gate geometry authored per track. 0 is start/finish. */
UCLASS()
class ROADTOF1_API ARaceTrackGate : public AActor
{
    GENERATED_BODY()
public:
    ARaceTrackGate();
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Race") int32 Order = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Race") TObjectPtr<class UBoxComponent> GateBounds;
};
