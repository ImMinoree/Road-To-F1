#include "RaceTrackGate.h"
#include "Components/BoxComponent.h"
ARaceTrackGate::ARaceTrackGate()
{
    GateBounds = CreateDefaultSubobject<UBoxComponent>(TEXT("GateBounds"));
    SetRootComponent(GateBounds);
    GateBounds->SetBoxExtent(FVector(30, 480, 200));
    GateBounds->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
