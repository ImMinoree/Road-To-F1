#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "KartNavigationMath.h"
#include "KartNavigationMap.generated.h"
class UTrackEdgeRoute;class UCanvas;class UFont;class AProofPawn;class APlayerController;

/** Navigation presentation only. Reuses the actual race edge asset, without scene capture. */
UCLASS(ClassGroup=(Kart),meta=(BlueprintSpawnableComponent))
class ROAD_TO_F1_NEW_API UKartNavigationMap : public UActorComponent {
 GENERATED_BODY()
public:
 UKartNavigationMap();
 virtual void BeginPlay() override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 void Draw(UCanvas* Canvas,UFont* Font);
 UFUNCTION(BlueprintCallable,Category="Navigation") void ToggleMap();
 UFUNCTION(BlueprintCallable,Category="Navigation") void CloseMap();
 UFUNCTION(BlueprintCallable,Category="Navigation") void ZoomIn();
 UFUNCTION(BlueprintCallable,Category="Navigation") void ZoomOut();
 UFUNCTION(BlueprintCallable,Category="Navigation") void RecenterMap();
 UFUNCTION(BlueprintCallable,Category="Navigation") void SetWaypointWorld(FVector Location);
 UFUNCTION(BlueprintCallable,Category="Navigation") void ClearWaypoint();
 UFUNCTION(BlueprintCallable,Category="Navigation") void PanMap(FVector2D WorldDelta);
 UFUNCTION(BlueprintPure,Category="Navigation") FVector2D MapScreenPoint(FVector Location)const{return FullView.Project(FVector2D(Location));}
 UFUNCTION(BlueprintPure,Category="Navigation") bool IsMapOpen()const{return bMapOpen;}
 UPROPERTY(VisibleInstanceOnly,BlueprintReadOnly,Category="Navigation") bool bHasWaypoint=false;
 UPROPERTY(VisibleInstanceOnly,BlueprintReadOnly,Category="Navigation") FVector WaypointWorld=FVector::ZeroVector;
 UPROPERTY(VisibleInstanceOnly,BlueprintReadOnly,Category="Navigation") float WaypointDistanceMeters=0;
 UPROPERTY(VisibleInstanceOnly,BlueprintReadOnly,Category="Navigation") float FullMapZoom=1;
 UPROPERTY(VisibleInstanceOnly,BlueprintReadOnly,Category="Navigation") int32 DisplayedKartCount=0;
 const UTrackEdgeRoute* GetRoute()const{return Route;}
private:
 UPROPERTY() TObjectPtr<UTrackEdgeRoute> Route;
 TWeakObjectPtr<APlayerController> Player;
 TArray<TWeakObjectPtr<AProofPawn>> Karts;
 FBox2D WorldBounds=FBox2D(ForceInit);KartNavigation::FView FullView;
 FVector2D PanCenter=FVector2D::ZeroVector,StartPoint=FVector2D(5000,82.4176712),PitPoint=FVector2D::ZeroVector;
 KartNavigation::FRoutePoint Waypoint;
 bool bMapOpen=false,bPausedByMap=false,bPreviousCursor=false,bHasPits=false;
 double LastKartRefresh=-1;
 void ZoomBy(float Factor);void PickWaypoint();void PanNorth();void PanSouth();void PanWest();void PanEast();
 void DrawTrack(UCanvas*,const KartNavigation::FView&,float Scale);
 void DrawBlips(UCanvas*,UFont*,const KartNavigation::FView&,AProofPawn*,float Scale,bool Full);
};
