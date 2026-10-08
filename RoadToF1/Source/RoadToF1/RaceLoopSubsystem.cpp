#include "RaceLoopSubsystem.h"
#include "RaceLoopWidget.h"
#include "RaceTrackGate.h"
#include "KartPawn.h"
#include "KartRaceDirector.h"
#include "RoadToF1.h"
#include "Components/BoxComponent.h"
#include "Components/InputComponent.h"
#include "Components/PrimitiveComponent.h"
#include "Components/TextRenderComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "WheeledVehiclePawn.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerStart.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "DrawDebugHelpers.h"

bool URaceLoopSubsystem::DoesSupportWorldType(EWorldType::Type Type) const
{
    return Type == EWorldType::Game || Type == EWorldType::PIE;
}

void URaceLoopSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
    Super::OnWorldBeginPlay(InWorld);
    Progress.Reset(TargetLaps, CheckpointLocations.Num());
    DiscoverTrack();
}

void URaceLoopSubsystem::DiscoverTrack()
{
    const bool bKartTrack = GetWorld()->GetMapName().EndsWith(TEXT("SouthGarda_KartRace"));
    if (!bKartTrack && !GetWorld()->GetMapName().EndsWith(TEXT("RacePrototype"))) return;
    if (bKartTrack)
    {
        TArray<ARaceTrackGate*> AuthoredGates;
        for (TActorIterator<ARaceTrackGate> It(GetWorld()); It; ++It) AuthoredGates.Add(*It);
        AuthoredGates.Sort([](const ARaceTrackGate& A, const ARaceTrackGate& B) { return A.Order < B.Order; });
        if (AuthoredGates.Num() < 2) { StatusMessage = TEXT("Track needs start and checkpoints."); return; }
        for (int32 Index = 0; Index < AuthoredGates.Num(); ++Index)
            if (AuthoredGates[Index]->Order != Index) { StatusMessage = TEXT("Track gate orders must be unique and consecutive."); return; }
        APlayerStart* Start = nullptr;
        for (TActorIterator<APlayerStart> It(GetWorld()); It; ++It) { Start = *It; break; }
        if (!Start) { StatusMessage = TEXT("PlayerStart missing: race disabled."); return; }
        RestartTransform = Start->GetActorTransform();
        for (ARaceTrackGate* Actor : AuthoredGates)
        {
            FRaceGateGeometry Gate;
            Gate.Transform = Actor->GateBounds->GetComponentTransform();
            Gate.Extent = Actor->GateBounds->GetScaledBoxExtent();
            Gates.Add(Gate);
        }
        Progress.Reset(TargetLaps, Gates.Num() - 1);
    }
    else
    {
    UBoxComponent* StartBox = nullptr;
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
    {
        if (It->GetClass()->GetPathName() != TEXT("/Game/Blueprints/BP_StartFinish.BP_StartFinish_C")) continue;
        TArray<UBoxComponent*> Boxes;
        It->GetComponents(Boxes);
        for (UBoxComponent* Box : Boxes)
        {
            if (Box->GetFName() == TEXT("StartFinishTrigger"))
            {
                if (StartBox) { StatusMessage = TEXT("Multiple start/finish triggers: race disabled."); return; }
                StartBox = Box;
            }
        }
    }
    if (!StartBox) return; // World Partition may stream the actor in on a later frame.
    if (CheckpointLocations.IsEmpty() || CheckpointLocations.Num() != CheckpointYaw.Num())
    {
        StatusMessage = TEXT("Checkpoint configuration is missing or invalid.");
        return;
    }
    APlayerStart* Start = nullptr;
    for (TActorIterator<APlayerStart> It(GetWorld()); It; ++It) { Start = *It; break; }
    if (!Start) { StatusMessage = TEXT("PlayerStart missing: race disabled."); return; }
    RestartTransform = Start->GetActorTransform();
    FRaceGateGeometry StartGate;
    FVector Direction = StartBox->GetForwardVector();
    if (FVector::DotProduct(Direction, Start->GetActorForwardVector()) < 0) Direction *= -1;
    StartGate.Transform = FTransform(Direction.Rotation(), StartBox->GetComponentLocation());
    StartGate.Extent = StartBox->GetScaledBoxExtent();
    Gates.Add(StartGate);
    for (int32 Index = 0; Index < CheckpointLocations.Num(); ++Index)
    {
        FRaceGateGeometry Gate;
        Gate.Transform = FTransform(FRotator(0, CheckpointYaw[Index], 0), CheckpointLocations[Index]);
        Gates.Add(Gate);
    }
    }
    bReady = true;
    StatusMessage = TEXT("Cross START to begin");
    for (int32 Index = 0; Index < Gates.Num(); ++Index)
    {
        const auto& Gate = Gates[Index];
        AActor* Marker = GetWorld()->SpawnActor<AActor>();
        UTextRenderComponent* Text = NewObject<UTextRenderComponent>(Marker);
        Marker->SetRootComponent(Text);
        Marker->AddInstanceComponent(Text);
        Text->SetText(FText::FromString(Index == 0 ? TEXT("START / FINISH") : FString::Printf(TEXT("CP%d"), Index)));
        Text->SetHorizontalAlignment(EHTA_Center);
        Text->SetWorldSize(120);
        Text->RegisterComponent();
        Marker->SetActorLocation(Gate.Transform.GetLocation() + FVector(0, 0, 650));
        Marker->SetActorRotation((-Gate.Transform.GetUnitAxis(EAxis::X)).Rotation());
        GateMarkers.Add(Marker);
    }
    UE_LOG(LogRoadToF1, Display, TEXT("Race loop ready: %d laps, %d ordered checkpoints."), Progress.TargetLaps, Progress.CheckpointCount);
}

void URaceLoopSubsystem::AttachPlayer()
{
    APlayerController* PC = UGameplayStatics::GetPlayerController(GetWorld(), 0);
    if (!PC || !PC->IsLocalController()) return;
    if (AttachedController != PC)
    {
        if (RaceWidget) RaceWidget->RemoveFromParent();
        if (RaceInput && AttachedController.IsValid()) AttachedController->PopInputComponent(RaceInput);
        AttachedController = PC;
        RaceInput = NewObject<UInputComponent>(PC, TEXT("RaceLoopInput"));
        RaceInput->RegisterComponent();
        RaceInput->Priority = 10;
        RaceInput->BindKey(EKeys::F5, IE_Pressed, this, &URaceLoopSubsystem::RestartRace);
        PC->PushInputComponent(RaceInput);
        RaceWidget = CreateWidget<URaceLoopWidget>(PC);
        if (RaceWidget)
        {
            RaceWidget->AddToPlayerScreen(10);
            RaceWidget->SetDesiredSizeInViewport(FVector2D(420, GetWorld()->GetMapName().EndsWith(TEXT("SouthGarda_KartRace")) ? 550 : 420));
            RaceWidget->SetPositionInViewport(FVector2D(28, 28));
        }
    }
    if (TrackedPawn != PC->GetPawn())
    {
        TrackedPawn = PC->GetPawn();
        Progress.Reset(TargetLaps, bReady ? Gates.Num() - 1 : CheckpointLocations.Num());
        bHavePreviousPosition = false; // Respawn must not inherit a previous vehicle's lap/position.
    }
}

void URaceLoopSubsystem::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (!GetWorld()->GetMapName().EndsWith(TEXT("RacePrototype")) && !GetWorld()->GetMapName().EndsWith(TEXT("SouthGarda_KartRace"))) return;
    if (!bReady) DiscoverTrack();
    AttachPlayer();
    if (!bReady || !TrackedPawn.IsValid()) return;
    const FVector Current = TrackedPawn->GetActorLocation();
    const double Now = GetWorld()->GetTimeSeconds();
    // Recovery/teleports reseed the sample rather than sweeping across half the circuit.
    const double MaxTravel = FMath::Max(1000.0, 15000.0 * static_cast<double>(DeltaTime));
    if (bHavePreviousPosition && !Progress.bFinished && FVector::Dist(PreviousPosition, Current) <= MaxTravel)
    {
        struct FCrossing { int32 Gate; double Fraction; };
        TArray<FCrossing> Crossings;
        for (int32 Index = 0; Index < Gates.Num(); ++Index)
        {
            double Fraction = 0;
            if (Gates[Index].ForwardCrossing(PreviousPosition, Current, Fraction)) Crossings.Add({Index, Fraction});
        }
        Crossings.Sort([](const FCrossing& A, const FCrossing& B) { return A.Fraction < B.Fraction; });
        for (const FCrossing& Crossing : Crossings)
        {
            if (Progress.CrossGate(Crossing.Gate, FMath::Lerp(PreviousTime, Now, Crossing.Fraction)))
                UE_LOG(LogRoadToF1, Display, TEXT("Race gate %d accepted: completed laps %d, checkpoints %d, finished %d"), Crossing.Gate, Progress.CompletedLaps, Progress.NextCheckpoint, Progress.bFinished);
        }
    }
    PreviousPosition = Current;
    PreviousTime = Now;
    bHavePreviousPosition = true;
    RefreshGateMarkers();
}

void URaceLoopSubsystem::RefreshGateMarkers()
{
    const int32 Next = !Progress.bStarted || Progress.NextCheckpoint == Progress.CheckpointCount ? 0 : Progress.NextCheckpoint + 1;
    for (int32 Index = 0; Index < Gates.Num(); ++Index)
    {
        const FColor Color = Progress.bFinished ? FColor::Silver : Index == Next ? FColor::Green : FColor(90, 140, 190);
        const auto& Gate = Gates[Index];
        // A thin visible gate above the asphalt, spanning the same bounds as the crossing test.
        if (GetWorld()->GetMapName().EndsWith(TEXT("SouthGarda_KartRace")))
        {
            const FVector Center = Gate.Transform.GetLocation() - FVector(0, 0, 75);
            const FVector Side = Gate.Transform.GetUnitAxis(EAxis::Y) * Gate.Extent.Y;
            DrawDebugLine(GetWorld(), Center - Side, Center + Side, Color, false, 0, 0, 5);
        }
        else DrawDebugBox(GetWorld(), Gate.Transform.GetLocation() + FVector(0, 0, 250), FVector(10, Gate.Extent.Y, 250), Gate.Transform.GetRotation(), Color, false, 0, 0, 8);
        if (GateMarkers.IsValidIndex(Index))
            if (UTextRenderComponent* Text = Cast<UTextRenderComponent>(GateMarkers[Index]->GetRootComponent())) Text->SetTextRenderColor(Color);
    }
}

void URaceLoopSubsystem::RestartRace()
{
    if (!bReady) return;
    Progress.Reset(TargetLaps, Gates.Num() - 1);
    bHavePreviousPosition = false;
    if (APawn* Pawn = TrackedPawn.Get())
    {
        Pawn->SetActorTransform(RestartTransform, false, nullptr, ETeleportType::TeleportPhysics);
        if (AKartPawn* Kart = Cast<AKartPawn>(Pawn)) Kart->ResetKart();
        if (UPrimitiveComponent* Body = Cast<UPrimitiveComponent>(Pawn->GetRootComponent()))
        {
            Body->SetPhysicsLinearVelocity(FVector::ZeroVector);
            Body->SetPhysicsAngularVelocityInDegrees(FVector::ZeroVector);
        }
        if (AWheeledVehiclePawn* Vehicle = Cast<AWheeledVehiclePawn>(Pawn))
        {
            Vehicle->GetVehicleMovementComponent()->ResetVehicle();
        }
    }
    UE_LOG(LogRoadToF1, Display, TEXT("Race reset: timing and checkpoint progress cleared, vehicle returned to PlayerStart."));
    if (AKartRaceDirector* Director = Cast<AKartRaceDirector>(UGameplayStatics::GetActorOfClass(GetWorld(), AKartRaceDirector::StaticClass()))) Director->ResetField();
}

void URaceLoopSubsystem::Deinitialize()
{
    if (RaceWidget) RaceWidget->RemoveFromParent();
    if (RaceInput && AttachedController.IsValid()) AttachedController->PopInputComponent(RaceInput);
    RaceWidget = nullptr;
    RaceInput = nullptr;
    GateMarkers.Empty();
    Gates.Empty();
    Super::Deinitialize();
}
