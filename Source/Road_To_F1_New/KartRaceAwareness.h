#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "KartRaceAwareness.generated.h"
class UCanvas; class UFont; class AProofPawn; class UCameraComponent; class USceneCaptureComponent2D; class UTextureRenderTarget2D; class UTrackEdgeRoute;
UCLASS(ClassGroup=(Kart))
class ROAD_TO_F1_NEW_API UKartRaceAwareness : public UActorComponent {
 GENERATED_BODY()
public:
 UKartRaceAwareness();
 virtual void BeginPlay() override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 void Draw(UCanvas* Canvas,UFont* Font,bool Suppressed);
 UFUNCTION(BlueprintCallable) void BeginLookBack();
 UFUNCTION(BlueprintCallable) void EndLookBack();
 UFUNCTION(BlueprintCallable) void ToggleMirror(){bMirrorEnabled=!bMirrorEnabled;}
 UPROPERTY(EditAnywhere,Category="Rear view",meta=(ClampMin="1",ClampMax="30")) float MirrorHz=20;
 UPROPERTY(EditAnywhere,Category="Rear view") bool bMirrorEnabled=true;
 UPROPERTY(VisibleInstanceOnly,BlueprintReadOnly) bool bLookingBack=false;
 UPROPERTY(VisibleInstanceOnly,BlueprintReadOnly) int32 TrackedOpponentCount=0;
 UPROPERTY(VisibleInstanceOnly,BlueprintReadOnly) int32 RearCaptureCount=0;
 UPROPERTY(Transient,BlueprintReadOnly) TObjectPtr<UTextureRenderTarget2D> MirrorTarget;
private:
 UPROPERTY() TObjectPtr<UTrackEdgeRoute> Route;
 UPROPERTY(Transient) TObjectPtr<USceneCaptureComponent2D> Capture;
 UPROPERTY(Transient) TObjectPtr<UCameraComponent> BackCamera;
 TWeakObjectPtr<AProofPawn> Driver;
 bool bSuppressed=false;
 double LastCapture=-1;
 double WarningUntil[8]={};
 int32 WarningRisk[8]={};
 void AttachDriver(AProofPawn* Pawn);
 void SelectCamera(bool Rear);
};
