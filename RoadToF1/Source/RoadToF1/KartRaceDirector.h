#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RaceProgress.h"
#include "KartTrainingProfiles.h"
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
    float Aggression = 0;
    float CornerSkill = 1;
    float PreferredLane = 0;
    float DesiredLane = 0;
    float DecisionCooldown = 0;
    float TargetSpeed = 0;
    float DecisionSeconds = 2.5f;
};

struct FKartStanding
{
    int32 Position = 0, Number = 0, FinishPlace = 0, Lap = 0;
    FString Name;
    float SpeedKmh = 0;
    double Distance = 0;
    bool bPlayer = false, bIncident = false;
    FLinearColor Color;
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
    TArray<FKartStanding> GetStandings() const;
    double DistanceToLapFinishCm(const FVector& P, const FRaceProgress& Progress) const;
    FString GetCommentaryCaption() const;
    bool IsCommentaryPlaying() const;
    bool HasStarted() const { return bReleased; }
    const TArray<FKartOpponentState>& GetOpponents() const { return Opponents; }
    class UKartTrainingRecorder* GetTrainingRecorder() const { return TrainingRecorder; }
    bool HasLearnedStyles() const { return LearnedStyles.Num() == 19; }
    UPROPERTY(EditAnywhere, Category="Race") TArray<FVector> RoutePoints;
    UPROPERTY(EditAnywhere, Category="Race") TArray<FTransform> Grid;
private:
    void UpdateCommentary();
    void Announce(const TCHAR* Cue, const FString& Caption);
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UAudioComponent> CommentaryAudio;
    UPROPERTY(EditAnywhere, Category="Commentary") TMap<FName, TObjectPtr<class USoundBase>> CommentaryClips;
    FString CommentaryCaption;
    double CaptionUntil = 0, CommentaryCooldownUntil = 0;
    int32 AnnouncedLap = 0, PreviousPlayerPlace = 20;
    bool bAnnouncedFinish = false, bPreviousFire = false;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UKartTrainingRecorder> TrainingRecorder;
    TArray<FKartTrainingStyle> LearnedStyles;
    int32 NearestPoint(const FVector& P) const;
    FVector LanePoint(int32 Index, float Lane) const;
    double RaceDistance(const FVector& P, const FRaceProgress& Progress) const;
    TArray<FKartOpponentState> Opponents;
    bool bReleased = false;
    int32 FinishCount = 0;
    int32 PlayerFinishPlace = 0;
};
