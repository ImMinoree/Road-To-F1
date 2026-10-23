#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/GameModeBase.h"
#include "ProofPawn.generated.h"
class UCameraComponent;
class USphereComponent;
// Temporary swept kinematic driving. No production kart physics or cockpit claims.
UCLASS()
class ROAD_TO_F1_NEW_API AProofPawn : public APawn {
 GENERATED_BODY()
public:
 AProofPawn();
 virtual void Tick(float DeltaSeconds) override;
 virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
private:
 UPROPERTY() USphereComponent* Body;
 UPROPERTY() UCameraComponent* Camera;
 float Throttle=0,Steer=0,Speed=0;
 float TestTime=0,SampleTime=0; int32 SampleFrames=0;
 void Drive(float V){Throttle=V;}
 void Turn(float V){Steer=V;}
 void Reset();
};
UCLASS()
class ROAD_TO_F1_NEW_API AProofGameMode : public AGameModeBase {
 GENERATED_BODY()
public: AProofGameMode();
};
