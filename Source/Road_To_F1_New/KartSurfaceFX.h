#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "KartSurfaceFX.generated.h"
class UInstancedStaticMeshComponent;
UENUM(BlueprintType)
enum class EKartLooseSurface : uint8 { None, Grass, Dirt };

/** Cosmetic pooled rear-tire debris. Never changes grip, input or forces. */
UCLASS(ClassGroup=(Rendering),meta=(BlueprintSpawnableComponent))
class ROAD_TO_F1_NEW_API UKartSurfaceFX : public UActorComponent {
 GENERATED_BODY()
public:
 UKartSurfaceFX();
 virtual void BeginPlay() override;
 virtual void TickComponent(float Dt,ELevelTick Type,FActorComponentTickFunction* Tick) override;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Surface effects") bool bEnabled=true;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Surface effects",meta=(ClampMin="50")) float MinimumSpeedCm=120;
 UPROPERTY(EditAnywhere,Category="Surface effects") FVector RearLeft=FVector(-55,-53.5,-31);
 UPROPERTY(EditAnywhere,Category="Surface effects") FVector RearRight=FVector(-55,53.5,-31);
 UPROPERTY(EditAnywhere,Category="Surface effects",meta=(ClampMin="1000")) float EffectDistanceCm=6500;
 UPROPERTY(BlueprintReadOnly,Category="Surface effects") int32 EmittingWheels=0;
 UPROPERTY(BlueprintReadOnly,Category="Surface effects") int32 LiveParticles=0;
 UPROPERTY(BlueprintReadOnly,Category="Surface effects") int32 TotalEmitted=0;
 UPROPERTY(BlueprintReadOnly,Category="Surface effects") EKartLooseSurface LeftSurface=EKartLooseSurface::None;
 UPROPERTY(BlueprintReadOnly,Category="Surface effects") EKartLooseSurface RightSurface=EKartLooseSurface::None;
 static EKartLooseSurface ClassifyNames(const FString& Names);
private:
 struct FSpeck {FVector Position,Velocity; FRotator Rotation; float Age=0,Life=0,Size=1; int32 Kind=0,Index=0; bool bLive=false;};
 UPROPERTY(Transient) TArray<TObjectPtr<UInstancedStaticMeshComponent>> Pools;
 TArray<FSpeck> Specks;
 FVector PreviousPosition=FVector::ZeroVector;
 float PreviousSpeed=0,PreviousYaw=0,Credits[2]={0,0};
 int32 Cursor[3]={0,0,0};
 FRandomStream Random;
 bool bReady=false;
 void Emit(int32 Kind,const FVector& Contact,const FVector& Motion,float Speed,float Side);
 EKartLooseSurface Probe(const FVector& Local,FVector& Contact) const;
 void Animate(float Dt);
};
