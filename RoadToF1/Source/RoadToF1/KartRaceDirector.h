#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RaceProgress.h"
#include "KartRaceDirector.generated.h"

class AKartPawn;
struct FKartOpponentState
{
    TWeakObjectPtr<AKartPawn> Kart;
    FRaceProgress Progress;
    FVector Previous = FVector::ZeroVector;
    int32 FinishPlace = 0;
    int32 RouteIndex = 0;
    float Lane = 0;
    float StalledSeconds = 0;
    float RecoverySeconds = 0;
};

/** Authored route and 20-slot grid; opponents use the same swept kart movement. */
UCLASS()
class ROADTOF1_API AKartRaceDirector : public AActor
{
    GENERATED_BODY()
public:
    AKartRaceDirector();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    void ResetField();
    int32 GetPlayerPlace() const;
    bool HasStarted() const { return bReleased; }
    const TArray<FKartOpponentState>& GetOpponents() const { return Opponents; }
    UPROPERTY(EditAnywhere, Category="Race") TArray<FVector> RoutePoints;
    UPROPERTY(EditAnywhere, Category="Race") TArray<FTransform> Grid;
private:
    int32 NearestPoint(const FVector& P) const;
    FVector LanePoint(int32 Index, float Lane) const;
    double RaceDistance(const FVector& P, const FRaceProgress& Progress) const;
    TArray<FKartOpponentState> Opponents;
    bool bReleased = false;
    int32 FinishCount = 0;
    int32 PlayerFinishPlace = 0;
};
