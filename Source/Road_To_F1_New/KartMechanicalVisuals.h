#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "KartMechanicalVisuals.generated.h"
class UStaticMeshComponent;class USceneComponent;class USkeletalMeshComponent;class UPoseableMeshComponent;class UInstancedStaticMeshComponent;class UAnimSequence;
/** One collision-free rendering assembly; samples ProofPawn after its authoritative fixed simulation. */
UCLASS(ClassGroup=(Rendering))
class ROAD_TO_F1_NEW_API UKartMechanicalVisuals:public UActorComponent {
 GENERATED_BODY()
public:
 UKartMechanicalVisuals();
 virtual void BeginPlay()override;
 virtual void TickComponent(float Dt,ELevelTick Type,FActorComponentTickFunction* Tick)override;
 UPROPERTY(EditAnywhere,Category="Kart visuals") bool bEnabled=true;
 UPROPERTY(BlueprintReadOnly,Category="Kart visuals") bool bReady=false;
 UPROPERTY(BlueprintReadOnly,Category="Kart visuals") float ColumnDegrees=0;
 UPROPERTY(BlueprintReadOnly,Category="Kart visuals") float LeftSteeringDegrees=0;
 UPROPERTY(BlueprintReadOnly,Category="Kart visuals") float RightSteeringDegrees=0;
 UPROPERTY(BlueprintReadOnly,Category="Kart visuals") float MaximumRodErrorCm=0;
 UPROPERTY(BlueprintReadOnly,Category="Kart visuals") float RearRollingDegrees=0;
 UPROPERTY(BlueprintReadOnly,Category="Kart visuals") float ThrottlePedal=0;
 UPROPERTY(BlueprintReadOnly,Category="Kart visuals") float BrakePedal=0;
 UPROPERTY(BlueprintReadOnly,Category="Kart livery") int32 LiverySlot=0;
 UPROPERTY(BlueprintReadOnly,Category="Kart livery") FLinearColor KartColor;
 UPROPERTY(BlueprintReadOnly,Category="Kart livery") FLinearColor DriverColor;
private:
 void ApplyLivery(int32 Slot);
 UPROPERTY(Transient) TObjectPtr<USceneComponent> Root;
 UPROPERTY(Transient) TArray<TObjectPtr<UStaticMeshComponent>> Parts;
 UPROPERTY(Transient) TObjectPtr<USkeletalMeshComponent> Sampler;
 UPROPERTY(Transient) TObjectPtr<UPoseableMeshComponent> Driver;
 UPROPERTY(Transient) TObjectPtr<UPoseableMeshComponent> POV;
 UPROPERTY(Transient) TObjectPtr<UAnimSequence> Steering;
 UPROPERTY(Transient) TObjectPtr<UInstancedStaticMeshComponent> Chain;
 double RearPhase=0,FrontPhase[2]={0,0};
 UStaticMeshComponent* Add(const FString& Name,USceneComponent* Parent,const FVector& Location=FVector::ZeroVector);
 void PoseLeg(UPoseableMeshComponent* Mesh,const TCHAR* Side,const FVector& Pivot,float Degrees);
};
