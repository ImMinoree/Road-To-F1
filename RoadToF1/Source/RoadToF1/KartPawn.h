#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/GameModeBase.h"
#include "KartPawn.generated.h"

/** First playable kart: swept arcade movement on traced ground, using the authored art. */
UCLASS()
class ROADTOF1_API AKartPawn : public APawn
{
    GENERATED_BODY()
public:
    AKartPawn();
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    virtual FVector GetVelocity() const override { return GetActorForwardVector() * Speed; }
    void ResetKart();
    void SetDriveInput(float Throttle, float Steering, bool Brake = false);
    float GetSpeedKmh() const { return Speed * .036f; }
private:
    void BrakePressed() { bBrake = true; }
    void BrakeReleased() { bBrake = false; }
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UBoxComponent> Body;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class USpringArmComponent> Boom;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UCameraComponent> Camera;
    UPROPERTY(VisibleAnywhere) TArray<TObjectPtr<class UStaticMeshComponent>> Art;
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
