#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RaceProgress.h"
#include "KartTrainingProfiles.h"
#include "KartBattleState.h"
#include "KartRaceDirector.generated.h"

class AKartPawn;
enum class EKartPassPhase : uint8 { Follow, Consider, Committed, Passing, Clear };
// Opt-in development snapshot. Limits are cm/s; gaps are centre-to-centre cm.
struct FKartPaceDebug
{
    float Corner = 55.f/.036f, Traffic = 55.f/.036f, Obstruction = 55.f/.036f;
    float Guidance = 55.f/.036f, Recovery = 55.f/.036f;
    float Ahead = -1, RelativeSpeed = 0;
    const TCHAR* Reason = TEXT("Acceleration");
};
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
    float RecoveryCooldown = 0;
    float LaunchSeconds = 0;
    float LaunchDistance = 0;
    float ActualLane = 0;
    bool bQueued = false;
    float Aggression = 0;
    float CornerSkill = 1;
    float PreferredLane = 0;
    float DesiredLane = 0;
    float DecisionCooldown = 0;
    float TargetSpeed = 0;
    float DecisionSeconds = 2.5f;
    FKartPaceDebug Pace;
    FKartBattleState Battle;
    EKartPassPhase PassPhase = EKartPassPhase::Follow;
    TWeakObjectPtr<AKartPawn> PassTarget;
    float ConstrainedSeconds = 0, PassSeconds = 0;
    int32 PassAttempts = 0, CompletedPasses = 0;
    float FilteredTrafficSpeed = 55.f/.036f;
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
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    void ResetField();
    int32 GetPlayerPlace() const;
    TArray<FKartStanding> GetStandings() const;
    double DistanceToLapFinishCm(const FVector& P, const FRaceProgress& Progress) const;
    FString GetCommentaryCaption() const;
    bool IsCommentaryPlaying() const;
    bool HasStarted() const { return bReleased; }
    bool bPaceDiagnostics = false;
    const TArray<FKartOpponentState>& GetOpponents() const { return Opponents; }
    class UKartTrainingRecorder* GetTrainingRecorder() const { return TrainingRecorder; }
    bool HasLearnedStyles() const { return LearnedStyles.Num() == 19; }
    UPROPERTY(EditAnywhere, Category="Racecraft", meta=(ClampMin="10", ClampMax="100")) float TrafficSafetyMargin = 35.f;
    UPROPERTY(EditAnywhere, Category="Race") TArray<FVector> RoutePoints;
    UPROPERTY(EditAnywhere, Category="Race") TArray<FTransform> Grid;
private:
    void CaptureBattleDebug(float Dt);
    void FlushBattleDebug();
    FString BattleCapturePath, BattleBuffer;
    float BattleSampleClock = 0, BattleElapsed = 0;
    bool bBattleCapture = false;
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
