#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/HUD.h"
#include "RaceStartGantry.generated.h"
class UKartNavigationMap;
class UKartRaceAwareness;
class UStaticMesh; class UMaterialInterface; class UMaterialInstanceDynamic; class UFont;
class UStaticMeshComponent; class UInstancedStaticMeshComponent; class USoundBase;
UCLASS()
class ROAD_TO_F1_NEW_API ARaceStartGantry : public AActor {
 GENERATED_BODY()
public:
 ARaceStartGantry();
 virtual void OnConstruction(const FTransform& Transform) override;
 virtual void BeginPlay() override;
 UPROPERTY(EditAnywhere,Category="Start display") TObjectPtr<UStaticMesh> HousingMesh;
 UPROPERTY(EditAnywhere,Category="Start display") TObjectPtr<UStaticMesh> LensMesh;
 UPROPERTY(EditAnywhere,Category="Start display") TObjectPtr<UStaticMesh> FrameMesh;
 UPROPERTY(EditAnywhere,Category="Start display") TObjectPtr<UMaterialInterface> LensMaterial;
 UPROPERTY(EditAnywhere,Category="Start audio") TObjectPtr<USoundBase> CountdownSound;
 UPROPERTY(EditAnywhere,Category="Start audio") TObjectPtr<USoundBase> LightsOutSound;
 UPROPERTY(EditAnywhere,Category="Start audio") bool bEnableAudio=true;
 UPROPERTY(EditAnywhere,Category="Start display",meta=(ClampMin="0",ClampMax="5")) int32 PreviewRedLights=0;
 UPROPERTY(EditAnywhere,Category="Start display",meta=(ClampMin="1")) float LitEmission=1000.f;
 UFUNCTION(BlueprintCallable,CallInEditor,Category="Race start") void RefreshDisplay();
 void SetRedLightCount(int32 Count);
 void PlayCue(bool bLightsOut);
private:
 UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Housings;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> Frame;
 UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> Lenses;
 UPROPERTY(Transient) TArray<TObjectPtr<UMaterialInstanceDynamic>> LensInstances;
};
UCLASS()
class ROAD_TO_F1_NEW_API ARaceStartHUD : public AHUD {
 GENERATED_BODY()
public:
 ARaceStartHUD();
 virtual void DrawHUD() override;
private:
 UPROPERTY() TObjectPtr<UFont> CountdownFont;
 UPROPERTY(VisibleAnywhere,Category="Navigation") TObjectPtr<UKartNavigationMap> NavigationMap;
 UPROPERTY(VisibleAnywhere,Category="Awareness") TObjectPtr<UKartRaceAwareness> RaceAwareness;
};
