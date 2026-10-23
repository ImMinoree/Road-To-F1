#include "GridStartSlot.h"
#include "Components/CapsuleComponent.h"
AGridStartSlot::AGridStartSlot(const FObjectInitializer& ObjectInitializer):Super(ObjectInitializer){SetActorEnableCollision(false);GetCapsuleComponent()->SetCollisionProfileName(TEXT("NoCollision"));Tags.Add(TEXT("RaceGridSlot"));}

