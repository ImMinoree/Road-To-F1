#include "KartPawn.h"
#include "Camera/CameraComponent.h"
#include "Components/BoxComponent.h"
#include "Components/InputComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/CollisionProfile.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Components/PointLightComponent.h"
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
    const TCHAR* DriverNames[] = {TEXT("Suit"), TEXT("SuitAccent"), TEXT("Helmet"), TEXT("Visor"), TEXT("Boots"), TEXT("Gloves")};
    for (const TCHAR* Name : DriverNames)
    {
        UStaticMeshComponent* Piece = CreateDefaultSubobject<UStaticMeshComponent>(*FString::Printf(TEXT("Driver_%s"), Name));
        Piece->SetupAttachment(Body);
        Piece->SetRelativeLocation(FVector(0, 0, -22));
        Piece->SetRelativeRotation(FRotator(0, 90, 0));
        Piece->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        DriverArt.Add(Piece);
    }
    ConstructorHelpers::FObjectFinder<UStaticMesh> Cone(TEXT("/Engine/BasicShapes/Cone.Cone"));
    ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    for (int32 Index = 0; Index < 6; ++Index)
    {
        auto AddEffect = [&](const FString& Name, UStaticMesh* Mesh, auto& Array)
        {
            UStaticMeshComponent* Piece = CreateDefaultSubobject<UStaticMeshComponent>(*Name);
            Piece->SetupAttachment(Body);
            Piece->SetStaticMesh(Mesh);
            Piece->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            Piece->SetCastShadow(false);
            Piece->SetVisibility(false);
            Array.Add(Piece);
        };
        AddEffect(FString::Printf(TEXT("Flame%d"), Index), Cone.Object, Flames);
        AddEffect(FString::Printf(TEXT("Smoke%d"), Index), Sphere.Object, Smoke);
    }
    FireLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("IncidentLight"));
    FireLight->SetupAttachment(Body);
    FireLight->SetRelativeLocation(FVector(-45, 35, 50));
    FireLight->SetLightColor(FLinearColor(1.f, .18f, .01f));
    FireLight->SetAttenuationRadius(250);
    FireLight->SetCastShadows(false);
    FireLight->SetVisibility(false);
}

void AKartPawn::BeginPlay()
{
    Super::BeginPlay();
    for (UStaticMeshComponent* Piece : DriverArt)
    {
        const FString Name = Piece->GetName();
        Piece->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, *FString::Printf(TEXT("/Game/RoadToF1/Art/DriversV01/Meshes/%s.%s"), *Name, *Name)));
    }
    ConfigureRacer(0, false);
    UMaterialInterface* FlameMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/RoadToF1/Art/IncidentV01/M_Flame.M_Flame"));
    UMaterialInterface* SmokeMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/RoadToF1/Art/IncidentV01/M_Smoke.M_Smoke"));
    for (UStaticMeshComponent* Piece : Flames) if (FlameMat) Piece->SetMaterial(0, FlameMat);
    for (UStaticMeshComponent* Piece : Smoke) if (SmokeMat) Piece->SetMaterial(0, SmokeMat);
}

void AKartPawn::ConfigureRacer(int32 Index, bool bOpponent)
{
    SpeedLimitKmh = bOpponent ? 55 : 57;
    static const TCHAR* Names[] = {TEXT("YOU"), TEXT("Luca Rossi"), TEXT("Noah Weber"), TEXT("Maya Patel"), TEXT("Leo Martin"), TEXT("Eva Novak"), TEXT("Kai Tanaka"), TEXT("Zara Khan"), TEXT("Finn Walsh"), TEXT("Mila Costa"), TEXT("Theo Laurent"), TEXT("Aria Singh"), TEXT("Hugo Silva"), TEXT("Nina Berg"), TEXT("Owen Clarke"), TEXT("Sara Malik"), TEXT("Alex Chen"), TEXT("Isla Reed"), TEXT("Enzo Romano"), TEXT("Freya Olsen")};
    DriverName = Names[FMath::Clamp(Index, 0, 19)];
    KartNumber = bOpponent ? Index : 20;
    SuitColor = FLinearColor::MakeFromHSV8((Index * 97) % 256, 210, 235);
    const FLinearColor Accent = FLinearColor::MakeFromHSV8((Index * 97 + 100) % 256, Index % 2 ? 180 : 30, 255);
    for (UStaticMeshComponent* Piece : DriverArt)
        for (int32 Slot = 0; Slot < Piece->GetNumMaterials(); ++Slot)
            if (UMaterialInstanceDynamic* Mat = Piece->CreateAndSetMaterialInstanceDynamic(Slot))
                Mat->SetVectorParameterValue(TEXT("LiveryColor"), Piece->GetName() == TEXT("Driver_Suit") ? SuitColor : Accent);
    if (bOpponent)
    {
        Boom->SetComponentTickEnabled(false);
        Camera->Deactivate();
    }
}

int32 AKartPawn::GetDriverMeshCount() const
{
    int32 Count = 0;
    for (const UStaticMeshComponent* Piece : DriverArt) if (Piece->GetStaticMesh()) ++Count;
    return Count;
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
        UpdateIncident(Dt);
        FCollisionQueryParams Query(SCENE_QUERY_STAT(KartGround), false, this);
        FHitResult Ground;
        const FVector Position = GetActorLocation();
        const FCollisionObjectQueryParams GroundObjects(ECC_WorldStatic);
        bool bGrounded = GetWorld()->LineTraceSingleByObjectType(Ground, Position + FVector(0, 0, 50), Position - FVector(0, 0, 65), GroundObjects, Query)
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
                if (GetWorld()->LineTraceSingleByObjectType(Support, Probe + FVector(0, 0, 40), Probe - FVector(0, 0, 65), GroundObjects, Query)
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
        const bool bDisabled = FireSeconds > 0 || StunSeconds > 0;
        const float Throttle = bDisabled ? 0 : Forward - Reverse;
        if (bGrounded)
        {
            if (bDisabled || bBrake || (Speed * Throttle < 0)) Speed = FMath::FInterpConstantTo(Speed, 0.f, Dt, 1500.f);
            else if (!FMath::IsNearlyZero(Throttle)) Speed += Throttle * 300.f * Dt;
            else Speed = FMath::FInterpConstantTo(Speed, 0.f, Dt, 180.f);
            Speed = FMath::Clamp(Speed, -400.f, SpeedLimitKmh / .036f);
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
            if (Hit.Normal.Z < .55f)
            {
                if (AKartPawn* Other = Cast<AKartPawn>(Hit.GetActor()))
                {
                    const float Closing = FMath::Max(0., -FVector::DotProduct(GetVelocity() - Other->GetVelocity(), Hit.Normal));
                    if (Closing > 100)
                    {
                        ReceiveCollision(Closing, Hit.Normal);
                        Other->ReceiveCollision(Closing, -Hit.Normal);
                    }
                }
                Speed = 0;
            }
            else VerticalSpeed = 0;
        }
    }
}

void AKartPawn::ResetKart()
{
    Speed = VerticalSpeed = SmoothedSteering = YawRate = 0;
    FireSeconds = StunSeconds = CollisionCooldown = IncidentClock = 0;
    CollisionCount = 0;
    UpdateIncident(0);
    SetDriveInput(0, 0);
    Boom->bEnableCameraLag = false;
    Boom->TickComponent(0, LEVELTICK_All, nullptr);
    Boom->bEnableCameraLag = true;
}

void AKartPawn::ReceiveCollision(float ImpactSpeed, const FVector& Normal)
{
    if (CollisionCooldown > 0 || ImpactSpeed < 100) return;
    CollisionCooldown = 1;
    ++CollisionCount;
    Speed *= .25f;
    StunSeconds = FMath::Clamp(ImpactSpeed / 1500.f, .15f, 1.f);
    const float Side = FVector::DotProduct(Normal, GetActorRightVector());
    AddActorWorldRotation(FRotator(0, FMath::Clamp(Side * ImpactSpeed / 70.f, -12.f, 12.f), 0));
    if (ImpactSpeed >= 700) FireSeconds = 6;
}

void AKartPawn::UpdateIncident(float Dt)
{
    FireSeconds = FMath::Max(0.f, FireSeconds - Dt);
    StunSeconds = FMath::Max(0.f, StunSeconds - Dt);
    CollisionCooldown = FMath::Max(0.f, CollisionCooldown - Dt);
    IncidentClock += Dt;
    const bool bFire = FireSeconds > 0;
    for (int32 Index = 0; Index < Flames.Num(); ++Index)
    {
        const float Pulse = .75f + .25f * FMath::Sin(IncidentClock * 19 + Index * 2.1f);
        Flames[Index]->SetVisibility(bFire);
        Flames[Index]->SetRelativeLocation(FVector(-45 + (Index % 3 - 1) * 12, 35 + (Index / 3 - .5f) * 14, 15 + Pulse * 18));
        Flames[Index]->SetRelativeScale3D(FVector(.11f * Pulse, .11f * Pulse, .35f * Pulse));
        const float Rise = FMath::Fmod(IncidentClock * .55f + Index / 6.f, 1.f);
        Smoke[Index]->SetVisibility(bFire);
        Smoke[Index]->SetRelativeLocation(FVector(-45 - Rise * 20, 35, 35 + Rise * 110));
        Smoke[Index]->SetRelativeScale3D(FVector(.08f + Rise * .4f));
    }
    FireLight->SetVisibility(bFire);
    if (bFire) FireLight->SetIntensity(1500 + 500 * FMath::Sin(IncidentClock * 17));
}

AKartGameMode::AKartGameMode()
{
    DefaultPawnClass = AKartPawn::StaticClass();
}
