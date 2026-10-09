#include "KartTrainingRecorder.h"
#include "KartTrainingLearner.h"
#include "KartRaceDirector.h"
#include "KartPawn.h"
#include "RaceLoopSubsystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"

UKartTrainingRecorder::UKartTrainingRecorder()
{
    PrimaryComponentTick.bCanEverTick = true;
}

bool UKartTrainingRecorder::StartCapture()
{
    if (bRecording) return true;
    const AKartRaceDirector* Director = Cast<AKartRaceDirector>(GetOwner());
    const AKartPawn* Player = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0));
    if (!Director || !Player || Director->RoutePoints.Num() < 100) return false;
    TrackId = TEXT("SouthGarda_KartRace");
    SessionId = FGuid::NewGuid().ToString(EGuidFormats::Digits);
    const FString Folder = FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("Training/Telemetry"));
    if (!IFileManager::Get().MakeDirectory(*Folder, true)) return false;
    CapturePath = FPaths::Combine(Folder, SessionId + TEXT(".csv"));
    CandidatePath.Reset();
    const FString Header = TEXT("time_seconds,session_id,track_id,route_index,lane_cm,speed_kmh,throttle,steering,brake,collision_count,burning,curvature,nearest_ahead_cm,relative_speed_kmh,next_checkpoint,completed_laps,x_cm,y_cm,yaw_deg\n");
    if (!FFileHelper::SaveStringToFile(Header, *CapturePath, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM)) return false;
    Elapsed = LastSample = 0;
    SampleCount = CleanSamples = CornerSamples = StraightSamples = 0;
    SumSpeed = SumThrottle = SumLane = SumCornerSpeed = 0;
    PreviousContacts = Player->GetCollisionCount();
    Buffer.Reset();
    bRecording = true;
    Sample();
    UE_LOG(LogTemp, Display, TEXT("Training recording started: %s"), *CapturePath);
    return true;
}

bool UKartTrainingRecorder::Flush()
{
    if (Buffer.IsEmpty()) return true;
    if (!FFileHelper::SaveStringToFile(Buffer, *CapturePath, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), FILEWRITE_Append))
    {
        bRecording = false;
        UE_LOG(LogTemp, Error, TEXT("Training recording write failed: %s"), *CapturePath);
        return false;
    }
    Buffer.Reset();
    return true;
}

void UKartTrainingRecorder::StopCapture()
{
    if (!bRecording) return;
    bRecording = false;
    if (Flush()) WriteCandidate();
}

void UKartTrainingRecorder::ToggleCapture() { if (bRecording) StopCapture(); else StartCapture(); }
void UKartTrainingRecorder::RestartSessionIfActive() { if (bRecording) { StopCapture(); StartCapture(); } }
void UKartTrainingRecorder::EndPlay(const EEndPlayReason::Type Reason) { StopCapture(); Super::EndPlay(Reason); }

void UKartTrainingRecorder::TickComponent(float Dt, ELevelTick TickType, FActorComponentTickFunction* TickFunction)
{
    Super::TickComponent(Dt, TickType, TickFunction);
    if (!bRecording) return;
    Elapsed += FMath::Max(0.f, Dt);
    if (Elapsed - LastSample >= .1 - UE_SMALL_NUMBER)
    {
        LastSample = Elapsed;
        Sample(); // Do not invent interpolated samples during a game hitch.
    }
}

void UKartTrainingRecorder::Sample()
{
    const AKartRaceDirector* Director = Cast<AKartRaceDirector>(GetOwner());
    const AKartPawn* Player = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0));
    if (!Director || !Player) { StopCapture(); return; }
    const FVector P = Player->GetActorLocation();
    int32 Near = 0;
    double Best = TNumericLimits<double>::Max();
    const auto& Route = Director->RoutePoints;
    for (int32 Index = 0; Index < Route.Num(); ++Index)
    {
        const double Distance = FVector::DistSquared2D(P, Route[Index]);
        if (Distance < Best) { Best = Distance; Near = Index; }
    }
    const FVector Forward = (Route[(Near + 1) % Route.Num()] - Route[Near]).GetSafeNormal2D();
    const FVector Side(-Forward.Y, Forward.X, 0);
    const float Lane = FVector::DotProduct(P - Route[Near], Side);
    const FVector Next = (Route[(Near + 2) % Route.Num()] - Route[(Near + 1) % Route.Num()]).GetSafeNormal2D();
    const double Curvature = FMath::Acos(FMath::Clamp(FVector::DotProduct(Forward, Next), -1., 1.)) / FMath::Max(1., FVector::Dist2D(Route[Near], Route[(Near + 1) % Route.Num()]));
    float Ahead = TNumericLimits<float>::Max(), Relative = 0;
    for (const auto& Opponent : Director->GetOpponents()) if (const AKartPawn* Other = Opponent.Kart.Get())
    {
        const FVector Delta = Other->GetActorLocation() - P;
        const float Gap = FVector::DotProduct(Delta, Forward);
        if (Gap > 0 && Gap < Ahead && Gap < 10000 && FMath::Abs(FVector::DotProduct(Delta, Side)) < 500)
        { Ahead = Gap; Relative = Player->GetSpeedKmh() - Other->GetSpeedKmh(); }
    }
    const URaceLoopSubsystem* Race = GetWorld()->GetSubsystem<URaceLoopSubsystem>();
    const auto& Progress = Race->GetProgress();
    const FString Traffic = Ahead < 10000 ? FString::Printf(TEXT("%.3f,%.3f"), Ahead, Relative) : TEXT(",");
    Buffer += FString::Printf(TEXT("%.6f,%s,%s,%d,%.3f,%.3f,%.4f,%.4f,%d,%d,%d,%.8f,%s,%d,%d,%.3f,%.3f,%.3f\n"),
        Elapsed, *SessionId, *TrackId, Near, Lane, Player->GetSpeedKmh(), Player->GetThrottleInput(), Player->GetSteeringInput(),
        Player->IsBrakeHeld() ? 1 : 0, Player->GetCollisionCount(), Player->IsBurning() ? 1 : 0, Curvature, *Traffic,
        Progress.NextCheckpoint, Progress.CompletedLaps, P.X, P.Y, Player->GetActorRotation().Yaw);
    ++SampleCount;
    if (!Player->IsBurning() && Player->GetCollisionCount() == PreviousContacts && Player->GetSpeedKmh() > 5 && FMath::Abs(Lane) < 450)
    {
        ++CleanSamples;
        SumSpeed += Player->GetSpeedKmh(); SumThrottle += FMath::Max(0.f, Player->GetThrottleInput()); SumLane += Lane;
        if (Curvature >= .0002) { ++CornerSamples; SumCornerSpeed += Player->GetSpeedKmh(); }
        else ++StraightSamples;
    }
    PreviousContacts = Player->GetCollisionCount();
    if (SampleCount % 10 == 0) Flush();
}

void UKartTrainingRecorder::WriteCandidate()
{
    const int32 Seed = int32(GetTypeHash(SessionId) & 0x7fffffff);
    const FKartDrivingSummary Summary{CleanSamples, CornerSamples, StraightSamples, SumSpeed, SumThrottle, SumLane, SumCornerSpeed};
    const FString Json = FKartTrainingLearner::Propose(TrackId, Seed, Summary);
    if (Json.IsEmpty()) return;
    CandidatePath = FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("Training"), TEXT("candidate_profiles_") + SessionId + TEXT(".json"));
    if (!FFileHelper::SaveStringToFile(Json, *CandidatePath, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM)) CandidatePath.Reset();
}
