#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "LocalKartDriverVisuals.generated.h"

class UCameraComponent;
class UMeshComponent;
class USceneComponent;
class USkeletalMesh;
class USkeletalMeshComponent;
class UStaticMesh;
class UStaticMeshComponent;
class UAnimSequence;

/** Local cockpit cosmetics only. Never supplies input, collision, movement or replicated state. */
UCLASS(ClassGroup=(Rendering), meta=(BlueprintSpawnableComponent))
class ROAD_TO_F1_NEW_API ULocalKartDriverVisuals : public UActorComponent
{
 GENERATED_BODY()
public:
 ULocalKartDriverVisuals();
 virtual void BeginPlay() override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

 UFUNCTION(BlueprintCallable, Category="Player visuals") void SetSteeringInput(float Input);
 UFUNCTION(BlueprintCallable, Category="Player visuals") void SetCockpitEnabled(bool bEnabled);
 /** Explicit opt-in: never guesses which kart/world meshes should be hidden. */
 UFUNCTION(BlueprintCallable, Category="Player visuals") void SetThirdPersonDriver(UMeshComponent* Mesh);
 UFUNCTION(BlueprintPure, Category="Player visuals") bool IsFirstPersonActive() const { return bActiveForLocalPlayer; }
 bool IsEligibleLocalHuman() const;
 USkeletalMeshComponent* GetFirstPersonArms() const { return Arms; }
 UStaticMeshComponent* GetFirstPersonWheel() const { return Wheel; }

 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Player visuals") bool bCockpitEnabled=true;
 UPROPERTY(EditAnywhere, Category="Player visuals") TSoftObjectPtr<USkeletalMesh> ArmsAsset;
 UPROPERTY(EditAnywhere, Category="Player visuals") TSoftObjectPtr<UAnimSequence> SteeringAsset;
 UPROPERTY(EditAnywhere, Category="Player visuals") TSoftObjectPtr<UStaticMesh> WheelAsset;
 /** Camera-relative art alignment, independent of the pawn's collision/physics transform. */
 UPROPERTY(EditAnywhere, Category="Player visuals") FTransform CockpitVisualTransform;
 UPROPERTY(EditAnywhere, Category="Player visuals", meta=(ClampMin="1",ClampMax="25")) float MaximumSteeringDegrees=25.f;
 UPROPERTY(EditAnywhere, Category="Player visuals") FName ThirdPersonDriverTag=TEXT("ThirdPersonDriver");

private:
 UPROPERTY(Transient) TObjectPtr<USceneComponent> VisualRoot;
 UPROPERTY(Transient) TObjectPtr<USkeletalMeshComponent> Arms;
 UPROPERTY(Transient) TObjectPtr<UStaticMeshComponent> Wheel;
 UPROPERTY(Transient) TObjectPtr<UMeshComponent> ThirdPersonDriver;
 UPROPERTY(Transient) TObjectPtr<UAnimSequence> ActiveSteeringSequence;
 bool bOriginalOwnerNoSee=false, bOriginalCaptured=false;
 bool bActiveForLocalPlayer=false, bLoadAttempted=false;
 float SteeringInput=0.f;
#if !UE_BUILD_SHIPPING
 float CaptureElapsed=0.f;
 int32 CaptureStage=0;
#endif
 void RefreshVisibility();
 bool CreateLocalVisuals(UCameraComponent* Camera);
 void RestoreThirdPersonVisibility();
};
