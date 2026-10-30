#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "KartSpeedLines.generated.h"
class UCameraComponent;class UMaterialInterface;class UMaterialInstanceDynamic;class ULocalKartDriverVisuals;
UCLASS(ClassGroup=(Kart))
class ROAD_TO_F1_NEW_API UKartSpeedLines : public UActorComponent {
 GENERATED_BODY()
public:
 UKartSpeedLines();
 virtual void BeginPlay() override;
 virtual void TickComponent(float Dt,ELevelTick Type,FActorComponentTickFunction* Function) override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 UFUNCTION(BlueprintCallable,Category="Speed lines") void ToggleSpeedVisuals();
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed lines") bool bEnabled=true;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed lines",meta=(ClampMin="0",ClampMax="2")) float Intensity=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed lines",meta=(ClampMin="8",ClampMax="160")) int32 StreakCount=80;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed lines",meta=(ClampMin="0.3",ClampMax="3")) float ThicknessPixels=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed lines",meta=(ClampMin="0",ClampMax="0.7")) float Opacity=.42f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed lines",meta=(ClampMin="0.1",ClampMax="3")) float AnimationSpeed=.8f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed lines") FVector2D VanishingPoint=FVector2D(.5,.42);
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed lines") float StartKmh=19;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed lines") float NoticeableKmh=34;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed lines") float StrongKmh=49;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed lines") float FullKmh=61;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed lines",meta=(ClampMin="0",ClampMax="1")) float PeripheralBlur=.15f;
 UPROPERTY(VisibleInstanceOnly,BlueprintReadOnly,Category="Speed lines") float ActualSpeedKmh=0;
 UPROPERTY(VisibleInstanceOnly,BlueprintReadOnly,Category="Speed lines") float SmoothedStrength=0;
 UPROPERTY(Transient,BlueprintReadOnly,Category="Speed lines") TObjectPtr<UMaterialInstanceDynamic> MaterialInstance;
private:
 UPROPERTY() TObjectPtr<UMaterialInterface> Material;
 TWeakObjectPtr<UCameraComponent> Camera;
 TWeakObjectPtr<ULocalKartDriverVisuals> ExistingVisuals;
 bool bSavedExistingEnabled=true,bOwnsExistingToggle=false;
 double PhaseSeconds=0;
 void Detach();
};
