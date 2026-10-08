#include "KartRaceDirector.h"
#include "KartPawn.h"
#include "RaceLoopSubsystem.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

AKartRaceDirector::AKartRaceDirector()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AKartRaceDirector::BeginPlay()
{
    Super::BeginPlay();
    if (RoutePoints.Num() < 100 || Grid.Num() != 20) return;
    for (int32 Index = 0; Index < 19; ++Index)
    {
        FActorSpawnParameters Params;
        Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        AKartPawn* Kart = GetWorld()->SpawnActor<AKartPawn>(AKartPawn::StaticClass(), Grid[Index], Params);
        Kart->ConfigureRacer(Index + 1, true);
        Kart->AddTickPrerequisiteActor(this);
        FKartOpponentState State;
        State.Kart = Kart;
        Opponents.Add(State);
    }
    ResetField();
}

void AKartRaceDirector::ResetField()
{
    bReleased = false;
    FinishCount = PlayerFinishPlace = 0;
    const URaceLoopSubsystem* Race = GetWorld()->GetSubsystem<URaceLoopSubsystem>();
    const int32 Laps = Race ? Race->GetProgress().TargetLaps : 3;
    const int32 Checkpoints = Race && Race->IsRaceAvailable() ? Race->GetGates().Num() - 1 : 12;
    for (int32 Index = 0; Index < Opponents.Num(); ++Index)
    {
        auto& State = Opponents[Index];
        State.Progress.Reset(Laps, Checkpoints);
        State.FinishPlace = 0;
        State.Lane = Index % 2 ? 130.f : -130.f;
        State.StalledSeconds = State.RecoverySeconds = 0;
        if (AKartPawn* Kart = State.Kart.Get())
        {
            Kart->SetActorTransform(Grid[Index], false, nullptr, ETeleportType::TeleportPhysics);
            Kart->ResetKart();
            State.Previous = Kart->GetActorLocation();
            State.RouteIndex = NearestPoint(State.Previous);
        }
    }
}

int32 AKartRaceDirector::NearestPoint(const FVector& P) const
{
    int32 Best = 0;
    double Distance = TNumericLimits<double>::Max();
    for (int32 Index = 0; Index < RoutePoints.Num(); ++Index)
    {
        const double D = FVector::DistSquared2D(P, RoutePoints[Index]);
        if (D < Distance) { Distance = D; Best = Index; }
    }
    return Best;
}

FVector AKartRaceDirector::LanePoint(int32 Index, float Lane) const
{
    const int32 N = RoutePoints.Num();
    Index = (Index + N) % N;
    const FVector Tangent = (RoutePoints[(Index + 1) % N] - RoutePoints[(Index + N - 1) % N]).GetSafeNormal2D();
    return RoutePoints[Index] + FVector(-Tangent.Y, Tangent.X, 0) * Lane;
}

void AKartRaceDirector::Tick(float Dt)
{
    Super::Tick(Dt);
    AKartPawn* Player = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0));
    URaceLoopSubsystem* Race = GetWorld()->GetSubsystem<URaceLoopSubsystem>();
    if (!Player || !Race || !Race->IsRaceAvailable() || RoutePoints.IsEmpty()) return;
    if (FMath::Abs(Player->GetSpeedKmh()) > .5f) bReleased = true;
    if (Race->GetProgress().bFinished && PlayerFinishPlace == 0) PlayerFinishPlace = ++FinishCount;
    const auto& Gates = Race->GetGates();
    for (int32 Agent = 0; Agent < Opponents.Num(); ++Agent)
    {
        auto& State = Opponents[Agent];
        AKartPawn* Kart = State.Kart.Get();
        if (!Kart) continue;
        const FVector P = Kart->GetActorLocation();
        for (int32 Gate = 0; Gate < Gates.Num(); ++Gate)
        {
            double Fraction;
            if (Gates[Gate].ForwardCrossing(State.Previous, P, Fraction))
                State.Progress.CrossGate(Gate, GetWorld()->GetTimeSeconds());
        }
        State.Previous = P;
        if (State.Progress.bFinished && State.FinishPlace == 0) State.FinishPlace = ++FinishCount;
        if (!bReleased) { Kart->SetDriveInput(0, 0, true); continue; }
        // Follow contiguous route samples, never the globally nearest adjoining
        // section at hairpins. The global search is used only for grid seeding.
        int32 Near = State.RouteIndex;
        double Closest = TNumericLimits<double>::Max();
        for (int32 Offset = -5; Offset <= 15; ++Offset)
        {
            const int32 Candidate = (State.RouteIndex + Offset + RoutePoints.Num()) % RoutePoints.Num();
            const double Distance = FVector::DistSquared2D(P, RoutePoints[Candidate]);
            if (Distance < Closest) { Closest = Distance; Near = Candidate; }
        }
        State.RouteIndex = Near;
        const float Speed = FMath::Abs(Kart->GetSpeedKmh()) / .036f;
        const float Spacing = FVector::Dist2D(RoutePoints[0], RoutePoints[1]);
        const int32 Look = FMath::Clamp(FMath::RoundToInt((280 + Speed * .3f) / Spacing), 2, 5);
        float Lane = State.Lane;
        float TargetSpeed = 55.f / .036f;
        // Anticipate curvature before reaching a bend. Limit lateral acceleration
        // and yaw demand to values the shared kart controller can actually turn.
        for (int32 Step = 2; Step <= 12; ++Step)
        {
            const FVector A = LanePoint(Near + Step - 1, Lane);
            const FVector B = LanePoint(Near + Step, Lane);
            const FVector C = LanePoint(Near + Step + 1, Lane);
            const double Angle = FMath::Acos(FMath::Clamp(FVector::DotProduct((B - A).GetSafeNormal2D(), (C - B).GetSafeNormal2D()), -1., 1.));
            const float Radius = FVector::Dist2D(A, B) / FMath::Max(Angle, .0001);
            const float BendSpeed = FMath::Min(FMath::Sqrt(420.f * Radius), .7f * Radius);
            const float AllowedHere = FMath::Sqrt(BendSpeed * BendSpeed + 2 * 700.f * Spacing * FMath::Max(0, Step - 2));
            TargetSpeed = FMath::Min(TargetSpeed, AllowedHere);
        }
        // Keep a gap behind the kart ahead. Use the free alternate lane when
        // possible, rather than driving straight into a stopped racer.
        bool bTraffic = false;
        bool bOtherLaneFree = true;
        auto Inspect = [&](AKartPawn* Other)
        {
            if (!Other || Other == Kart) return;
            const FVector Local = Kart->GetActorTransform().InverseTransformPosition(Other->GetActorLocation());
            if (Local.X > 0 && Local.X < 650 && FMath::Abs(Local.Y) < 160) { bTraffic = true; TargetSpeed = FMath::Min(TargetSpeed, FMath::Max(0.f, (Local.X - 240) * 2.f)); }
            if (FMath::Abs(Local.X) < 550 && Local.Y * Lane < 0 && FMath::Abs(Local.Y) < 450) bOtherLaneFree = false;
        };
        Inspect(Player);
        for (const auto& Other : Opponents) Inspect(Other.Kart.Get());
        if (bTraffic && bOtherLaneFree) State.Lane = Lane = -Lane;
        const FVector LocalTarget = Kart->GetActorTransform().InverseTransformPosition(LanePoint(Near + Look, Lane));
        const float Curvature = 2 * LocalTarget.Y / FMath::Max(1., LocalTarget.SizeSquared2D());
        const float Steering = FMath::Clamp(FMath::RadiansToDegrees(FMath::Atan(Curvature * 104)) * (1 + Speed / 1400) / 22, -1.f, 1.f);
        if (LocalTarget.X < 100 || FMath::Abs(FMath::Atan2(LocalTarget.Y, LocalTarget.X)) > .65f) TargetSpeed = FMath::Min(TargetSpeed, 250.f);
        State.StalledSeconds = Speed < 30 ? State.StalledSeconds + Dt : 0;
        if (State.StalledSeconds > 3 && State.RecoverySeconds <= 0)
        {
            State.RecoverySeconds = 1.2f;
            State.StalledSeconds = 0;
        }
        if (State.RecoverySeconds > 0)
        {
            State.RecoverySeconds -= Dt;
            Kart->SetDriveInput(-1, -Steering);
            continue;
        }
        Kart->SetDriveInput(Speed < TargetSpeed - 15 ? 1 : 0, Steering, Speed > TargetSpeed + 15);
    }
}

double AKartRaceDirector::RaceDistance(const FVector& P, const FRaceProgress& Progress) const
{
    const int32 Near = NearestPoint(P);
    const FVector Tangent = (RoutePoints[(Near + 1) % RoutePoints.Num()] - RoutePoints[Near]).GetSafeNormal2D();
    const double SubPoint = FVector::DotProduct(P - RoutePoints[Near], Tangent) / FVector::Dist2D(RoutePoints[Near], RoutePoints[(Near + 1) % RoutePoints.Num()]);
    double Fraction = (Near + SubPoint) / RoutePoints.Num();
    // The nearest sample wraps to zero just before the finish plane. Keep that
    // small negative projection at the end of a validated lap for standings.
    if (!Progress.bStarted) return Fraction > .5 ? Fraction - 1 : Fraction;
    if (Progress.NextCheckpoint == Progress.CheckpointCount && Fraction < .1) Fraction += 1;
    return Progress.CompletedLaps + Fraction;
}

int32 AKartRaceDirector::GetPlayerPlace() const
{
    if (!bReleased) return 20;
    if (PlayerFinishPlace) return PlayerFinishPlace;
    const AKartPawn* Player = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0));
    const URaceLoopSubsystem* Race = GetWorld()->GetSubsystem<URaceLoopSubsystem>();
    if (!Player || !Race || RoutePoints.IsEmpty()) return 20;
    const double PlayerDistance = RaceDistance(Player->GetActorLocation(), Race->GetProgress());
    int32 Place = 1;
    for (const auto& State : Opponents)
        if (const AKartPawn* Kart = State.Kart.Get())
            if (State.FinishPlace || RaceDistance(Kart->GetActorLocation(), State.Progress) > PlayerDistance) ++Place;
    return Place;
}
