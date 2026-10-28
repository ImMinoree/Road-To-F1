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
class UTextRenderComponent;
class UMaterialInterface;
class UMaterialInstanceDynamic;

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
 void UseMechanicalCamera(UCameraComponent* Camera);
 bool IsEligibleLocalHuman() const;
 USkeletalMeshComponent* GetFirstPersonArms() const { return Arms; }
 UStaticMeshComponent* GetFirstPersonWheel() const { return Wheel; }
 UStaticMeshComponent* GetKartChassis() const { return Chassis; }

 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Player visuals") bool bCockpitEnabled=true;
 /** Reversible reference-inspired local cockpit. False restores the preserved legacy cosmetics. */
 UPROPERTY(EditAnywhere, Category="Player visuals") bool bReferenceCockpit=true;
 UPROPERTY(EditAnywhere, Category="Player visuals") TSoftObjectPtr<USkeletalMesh> ArmsAsset;
 UPROPERTY(EditAnywhere, Category="Player visuals") TSoftObjectPtr<UAnimSequence> SteeringAsset;
 UPROPERTY(EditAnywhere, Category="Player visuals") TSoftObjectPtr<UStaticMesh> WheelAsset;
 UPROPERTY(EditAnywhere, Category="Player visuals") TSoftObjectPtr<UStaticMesh> ChassisAsset;
 /** Pawn-relative source-art ground alignment. Camera pitch never moves the seated kart or hands. */
 UPROPERTY(EditAnywhere, Category="Player visuals") FTransform CockpitVisualTransform;
 UPROPERTY(EditAnywhere, Category="Player visuals", meta=(ClampMin="1",ClampMax="25")) float MaximumSteeringDegrees=25.f;
 UPROPERTY(EditAnywhere, Category="Player visuals") FName ThirdPersonDriverTag=TEXT("ThirdPersonDriver");
 /** Cosmetic speed cues only; disabling restores the authored camera immediately. */
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Speed perception") bool bSpeedEffectsEnabled=true;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Speed perception", meta=(ClampMin="0",ClampMax="8")) float SpeedFOVBoost=6.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Speed perception", meta=(ClampMin="0",ClampMax="1")) float SpeedVibrationScale=1.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Speed perception", meta=(ClampMin="0",ClampMax="1")) float PeripheralBlurScale=1.f;
 UPROPERTY(EditAnywhere, Category="Speed perception") TSoftObjectPtr<UMaterialInterface> SpeedBlurAsset;

private:
 UPROPERTY(Transient) TObjectPtr<USceneComponent> VisualRoot;
 UPROPERTY(Transient) TObjectPtr<USkeletalMeshComponent> Arms;
 UPROPERTY(Transient) TObjectPtr<UStaticMeshComponent> Wheel;
 UPROPERTY(Transient) TObjectPtr<UStaticMeshComponent> Chassis;
 UPROPERTY(Transient) TObjectPtr<UMeshComponent> ThirdPersonDriver;
 UPROPERTY(Transient) TObjectPtr<UAnimSequence> ActiveSteeringSequence;
 UPROPERTY(Transient) TObjectPtr<UTextRenderComponent> DashboardSpeed;
 UPROPERTY(Transient) TObjectPtr<UTextRenderComponent> DashboardTime;
 FString LastDashboardSpeed,LastDashboardTime;
 bool bOriginalOwnerNoSee=false, bOriginalCaptured=false;
 bool bActiveForLocalPlayer=false, bLoadAttempted=false;
 float SteeringInput=0.f;
 bool bUsingLegacy=false,bCameraAdjusted=false;
 UPROPERTY(Transient) TObjectPtr<UCameraComponent> CockpitCamera;
 FTransform OriginalCameraTransform;
 float OriginalCameraFOV=90.f;
 UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> SpeedBlur;
 FTransform SpeedBaseTransform;
 float SpeedBaseFOV=90.f,SpeedBlend=0.f;
 double SpeedPhase=0;
 bool bSpeedCameraApplied=false;
 bool bMechanicalCamera=false;
 void RestoreSpeedCamera();
 void UpdateSpeedCamera(float DeltaTime);
 void ConfigureCockpitCamera(bool bActive);
#if !UE_BUILD_SHIPPING
 float CaptureElapsed=0.f;
 int32 CaptureStage=0;
#endif
 void RefreshVisibility();
 bool CreateLocalVisuals(UCameraComponent* Camera);
 void RestoreThirdPersonVisibility();
};

