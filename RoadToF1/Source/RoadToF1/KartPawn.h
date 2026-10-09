#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/GameModeBase.h"
#include "KartEngineSound.h"
#include "KartPawn.generated.h"

/** First playable kart: swept arcade movement on traced ground, using the authored art. */
UCLASS()
class ROADTOF1_API AKartPawn : public APawn
{
    GENERATED_BODY()
public:
    AKartPawn();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    virtual FVector GetVelocity() const override { return GetActorForwardVector() * Speed; }
    void ResetKart();
    void SetDriveInput(float Throttle, float Steering, bool Brake = false);
    float GetSpeedKmh() const { return Speed * .036f; }
    void ConfigureRacer(int32 Index, bool bOpponent);
    float GetSpeedLimitKmh() const { return SpeedLimitKmh; }
    FLinearColor GetSuitColor() const { return SuitColor; }
    int32 GetDriverMeshCount() const;
    const FString& GetDriverName() const { return DriverName; }
    int32 GetKartNumber() const { return KartNumber; }
    bool IsBurning() const { return FireSeconds > 0; }
    int32 GetCollisionCount() const { return CollisionCount; }
    float GetThrottleInput() const { return Forward - Reverse; }
    float GetSteeringInput() const { return Right - Left; }
    bool IsBrakeHeld() const { return bBrake; }
    void ReceiveCollision(float ImpactSpeed, const FVector& Normal);
private:
    void UpdateAudioAndNumber(float Dt);
    FKartEngineSound EngineSynth;
    UPROPERTY(Transient) TObjectPtr<class USoundWaveProcedural> EngineWave;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UAudioComponent> EngineAudio;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class USceneComponent> NumberBadge;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UStaticMeshComponent> NumberShell;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UStaticMeshComponent> NumberFace;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UTextRenderComponent> RacerNumber;
    void UpdateIncident(float Dt);
    void ToggleTrainingRecording();
    void BrakePressed() { bBrake = true; }
    void BrakeReleased() { bBrake = false; }
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UBoxComponent> Body;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class USpringArmComponent> Boom;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UCameraComponent> Camera;
    UPROPERTY(VisibleAnywhere) TArray<TObjectPtr<class UStaticMeshComponent>> Art;
    UPROPERTY(VisibleAnywhere) TArray<TObjectPtr<class UStaticMeshComponent>> DriverArt;
    UPROPERTY(VisibleAnywhere) TArray<TObjectPtr<class UStaticMeshComponent>> Flames;
    UPROPERTY(VisibleAnywhere) TArray<TObjectPtr<class UStaticMeshComponent>> Smoke;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UPointLightComponent> FireLight;
    FString DriverName = TEXT("YOU");
    int32 KartNumber = 20;
    float FireSeconds = 0, StunSeconds = 0, CollisionCooldown = 0, IncidentClock = 0;
    int32 CollisionCount = 0;
    float SpeedLimitKmh = 57;
    FLinearColor SuitColor = FLinearColor::Red;
    float Speed = 0;
    float VerticalSpeed = 0;
    float SmoothedSteering = 0;
    float YawRate = 0;
    float Forward = 0, Reverse = 0, Left = 0, Right = 0;
    bool bBrake = false;
};

UCLASS()
class ROADTOF1_API AKartGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AKartGameMode();
};
