#include "KartPawn.h"
#include "Camera/CameraComponent.h"
#include "Components/BoxComponent.h"
#include "Components/InputComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/CollisionProfile.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputCoreTypes.h"
#include "UObject/ConstructorHelpers.h"

AKartPawn::AKartPawn()
{
    PrimaryActorTick.bCanEverTick = true;
    Body = CreateDefaultSubobject<UBoxComponent>(TEXT("KartCollision"));
    SetRootComponent(Body);
    Body->SetBoxExtent(FVector(98, 63, 20));
    Body->SetCollisionProfileName(UCollisionProfile::Pawn_ProfileName);
    Body->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
    const TCHAR* Names[] = { TEXT("Chassis"), TEXT("Aluminium"), TEXT("Rubber"), TEXT("Fairing"), TEXT("Engine"), TEXT("White"), TEXT("Carbon"), TEXT("Chain") };
    for (const TCHAR* Name : Names)
    {
        UStaticMeshComponent* Piece = CreateDefaultSubobject<UStaticMeshComponent>(*FString::Printf(TEXT("Art_%s"), Name));
        Piece->SetupAttachment(Body);
        Piece->SetRelativeLocation(FVector(0, 0, -22));
        // Imported kart points along -Y; align it with the pawn's +X forward axis.
        Piece->SetRelativeRotation(FRotator(0, 90, 0));
        Piece->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        ConstructorHelpers::FObjectFinder<UStaticMesh> Asset(*FString::Printf(TEXT("/Game/RoadToF1/Art/SouthGardaV01/Meshes/Kart_%s.Kart_%s"), Name, Name));
        if (Asset.Succeeded()) Piece->SetStaticMesh(Asset.Object);
        Art.Add(Piece);
    }
    Boom = CreateDefaultSubobject<USpringArmComponent>(TEXT("FollowBoom"));
    Boom->SetupAttachment(Body);
    Boom->TargetArmLength = 430;
    Boom->SetRelativeLocation(FVector(0, 0, 85));
    Boom->SetRelativeRotation(FRotator(-15, 0, 0));
    Boom->bEnableCameraLag = true;
    Boom->CameraLagSpeed = 8;
    Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    Camera->SetupAttachment(Boom);
    Camera->FieldOfView = 80;
}

void AKartPawn::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    const auto BindHeldKey = [Input](FKey Key, float* Value)
    {
        FInputKeyBinding Press(FInputChord(Key), IE_Pressed);
        Press.KeyDelegate.GetDelegateForManualSet().BindLambda([Value]() { *Value = 1; });
        Input->KeyBindings.Add(Press);
        FInputKeyBinding Release(FInputChord(Key), IE_Released);
        Release.KeyDelegate.GetDelegateForManualSet().BindLambda([Value]() { *Value = 0; });
        Input->KeyBindings.Add(Release);
    };
    BindHeldKey(EKeys::W, &Forward);
    BindHeldKey(EKeys::S, &Reverse);
    BindHeldKey(EKeys::A, &Left);
    BindHeldKey(EKeys::D, &Right);
    Input->BindKey(EKeys::SpaceBar, IE_Pressed, this, &AKartPawn::BrakePressed);
    Input->BindKey(EKeys::SpaceBar, IE_Released, this, &AKartPawn::BrakeReleased);
}

void AKartPawn::SetDriveInput(float Throttle, float Steering, bool Brake)
{
    Forward = FMath::Max(0.f, FMath::Clamp(Throttle, -1.f, 1.f));
    Reverse = FMath::Max(0.f, -FMath::Clamp(Throttle, -1.f, 1.f));
    Right = FMath::Max(0.f, FMath::Clamp(Steering, -1.f, 1.f));
    Left = FMath::Max(0.f, -FMath::Clamp(Steering, -1.f, 1.f));
    bBrake = Brake;
}

void AKartPawn::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    // Bounded substeps keep swept movement, braking and steering stable during hitches.
    float Remaining = FMath::Min(DeltaSeconds, .25f);
    while (Remaining > UE_SMALL_NUMBER)
    {
        const float Dt = FMath::Min(Remaining, 1.f / 120.f);
        Remaining -= Dt;
        FCollisionQueryParams Query(SCENE_QUERY_STAT(KartGround), false, this);
        FHitResult Ground;
        const FVector Position = GetActorLocation();
        bool bGrounded = GetWorld()->LineTraceSingleByChannel(Ground, Position + FVector(0, 0, 50), Position - FVector(0, 0, 65), ECC_Visibility, Query)
            && Ground.Normal.Z > .55f && Position.Z - Ground.ImpactPoint.Z < 55;
        // Support the whole footprint, including its next movement. A centre-only
        // trace lowered the box onto grass while its nose still touched asphalt,
        // making the 6.5cm road edge behave like a wall. Limit climb to 12cm so
        // this cannot lift the kart over actual buildings or barriers.
        float SupportHeight = bGrounded ? Ground.ImpactPoint.Z : Position.Z - 22;
        if (bGrounded)
        {
            const FVector Ahead = GetActorForwardVector() * Speed * Dt;
            for (float X : {-98.f, 0.f, 98.f}) for (float Y : {-63.f, 0.f, 63.f})
            {
                const FVector Probe = Position + Ahead + GetActorForwardVector() * X + GetActorRightVector() * Y;
                FHitResult Support;
                if (GetWorld()->LineTraceSingleByChannel(Support, Probe + FVector(0, 0, 40), Probe - FVector(0, 0, 65), ECC_Visibility, Query)
                    && Support.Normal.Z > .55f && Support.ImpactPoint.Z <= Position.Z - 22 + 12)
                    SupportHeight = FMath::Max(SupportHeight, Support.ImpactPoint.Z);
            }
            const float Rise = SupportHeight + 22 - Position.Z;
            if (Rise > 0)
            {
                FHitResult Ceiling;
                AddActorWorldOffset(FVector(0, 0, Rise), true, &Ceiling);
            }
        }
        const float Throttle = Forward - Reverse;
        if (bGrounded)
        {
            if (bBrake || (Speed * Throttle < 0)) Speed = FMath::FInterpConstantTo(Speed, 0.f, Dt, 1500.f);
            else if (!FMath::IsNearlyZero(Throttle)) Speed += Throttle * 300.f * Dt;
            else Speed = FMath::FInterpConstantTo(Speed, 0.f, Dt, 180.f);
            Speed = FMath::Clamp(Speed, -400.f, 55.f / .036f);
            const float DesiredSteering = Right - Left;
            SmoothedSteering = FMath::FInterpTo(SmoothedSteering, DesiredSteering, Dt, FMath::IsNearlyZero(DesiredSteering) ? 5.f : 4.f);
            const float SteeringAngle = FMath::DegreesToRadians(SmoothedSteering * 22.f / (1.f + FMath::Abs(Speed) / 1400.f));
            const float DesiredYawRate = FMath::Clamp(FMath::RadiansToDegrees(Speed / 104.f * FMath::Tan(SteeringAngle)), -55.f, 55.f);
            YawRate = FMath::FInterpTo(YawRate, DesiredYawRate, Dt, 5.f);
            AddActorWorldRotation(FRotator(0, YawRate * Dt, 0));
            VerticalSpeed = 0;
        }
        else VerticalSpeed -= 980.f * Dt;
        FVector Delta = GetActorForwardVector() * Speed * Dt;
        Delta.Z = bGrounded ? SupportHeight + 22 - GetActorLocation().Z : VerticalSpeed * Dt;
        FHitResult Hit;
        AddActorWorldOffset(Delta, true, &Hit);
        if (Hit.bBlockingHit)
        {
            if (Hit.Normal.Z < .55f) Speed = 0;
            else VerticalSpeed = 0;
        }
    }
}

void AKartPawn::ResetKart()
{
    Speed = VerticalSpeed = SmoothedSteering = YawRate = 0;
    SetDriveInput(0, 0);
    Boom->bEnableCameraLag = false;
    Boom->TickComponent(0, LEVELTICK_All, nullptr);
    Boom->bEnableCameraLag = true;
}

AKartGameMode::AKartGameMode()
{
    DefaultPawnClass = AKartPawn::StaticClass();
}
