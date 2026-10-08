#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "Tests/AutomationEditorCommon.h"
#include "Tests/AutomationCommon.h"
#include "KartPawn.h"
#include "RaceLoopSubsystem.h"
#include "RaceLoopWidget.h"
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FVerifyKartTrack, FAutomationTestBase*, Test);
bool FVerifyKartTrack::Update()
{
    UWorld* World = AutomationCommon::GetAnyGameWorld();
    if (!World) { Test->AddError(TEXT("PIE world missing")); return true; }
    AKartPawn* Kart = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(World, 0));
    URaceLoopSubsystem* Race = World->GetSubsystem<URaceLoopSubsystem>();
    if (!Kart || !Race) { Test->AddError(TEXT("Playable kart or subsystem missing")); return true; }
    Race->Tick(0);
    Test->TestTrue(TEXT("Native track gates activate race"), Race->IsRaceAvailable());
    if (!Race->IsRaceAvailable()) return true;
    Test->TestEqual(TEXT("South Garda has 12 ordered checkpoints"), Race->GetGates().Num(), 13);
    TArray<UUserWidget*> Widgets;
    UWidgetBlueprintLibrary::GetAllWidgetsOfClass(World, Widgets, URaceLoopWidget::StaticClass(), false);
    Test->TestEqual(TEXT("Kart race HUD is present"), Widgets.Num(), 1);
    Race->RestartRace();
    const FVector Start = Kart->GetActorLocation();
    for (int32 Frame = 0; Frame < 180; ++Frame) { Kart->SetDriveInput(1, 0); Kart->Tick(1.f / 60.f); Race->Tick(1.f / 60.f); }
    Test->TestTrue(TEXT("Throttle drives kart along ground"), FVector::Dist2D(Start, Kart->GetActorLocation()) > 900);
    Test->TestTrue(TEXT("Physical movement crosses start and starts timing"), Race->GetProgress().bStarted);
    Test->TestTrue(TEXT("Kart stays at road height"), FMath::Abs(Kart->GetActorLocation().Z - 25) < 15);
    Test->TestTrue(TEXT("Throttle increases speed"), Kart->GetSpeedKmh() > 15);
    for (int32 Frame = 0; Frame < 120; ++Frame) { Kart->SetDriveInput(0, 0, true); Kart->Tick(1.f / 60.f); }
    Test->TestTrue(TEXT("Brake brings kart to rest"), FMath::Abs(Kart->GetSpeedKmh()) < .1f);
    Race->RestartRace();
    Kart->SetActorLocation(FVector(-12000, -5200, 24.5));
    Kart->SetActorRotation(FRotator::ZeroRotator);
    for (int32 Frame = 0; Frame < 600; ++Frame) { Kart->SetDriveInput(1, 0); Kart->Tick(1.f / 60.f); }
    Test->TestTrue(TEXT("Kart passes all grid boxes and finish paint without stopping"), Kart->GetActorLocation().X > -3000);
    Test->TestTrue(TEXT("Full throttle respects beginner speed limit"), Kart->GetSpeedKmh() <= 55.01f && Kart->GetSpeedKmh() > 50);
    const float BeforeTurn = Kart->GetActorRotation().Yaw;
    Kart->SetDriveInput(1, 1); Kart->Tick(1.f / 60.f);
    const float FirstTurn = FMath::FindDeltaAngleDegrees(BeforeTurn, Kart->GetActorRotation().Yaw);
    Test->TestTrue(TEXT("Digital steering ramps in rather than snapping"), FirstTurn > 0 && FirstTurn < .1f);
    const float AfterFirst = Kart->GetActorRotation().Yaw;
    Kart->Tick(1.f / 60.f);
    Test->TestTrue(TEXT("Steering response builds smoothly across frames"), FMath::FindDeltaAngleDegrees(AfterFirst, Kart->GetActorRotation().Yaw) > FirstTurn);
    Race->RestartRace();
    // Trace the entire exported centreline independently of the gate rules: verify that
    // the imported mesh offers a continuous drivable surface rather than just visuals.
    FString JsonText;
    TSharedPtr<FJsonObject> Manifest;
    const FString Path = FPaths::Combine(FPaths::ProjectDir(), TEXT("../Art/KartLab/exports/manifest.json"));
    if (!FFileHelper::LoadFileToString(JsonText, *Path) || !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(JsonText), Manifest))
        Test->AddError(TEXT("Track validation path missing"));
    else
    {
        int32 Unsupported = 0;
        FCollisionQueryParams Query(SCENE_QUERY_STAT(KartCircuitValidation), true, Kart);
        for (const auto& Point : Manifest->GetArrayField(TEXT("drivePath")))
        {
            const auto& Values = Point->AsArray();
            FVector P(Values[0]->AsNumber(), Values[1]->AsNumber(), 250);
            FHitResult Hit;
            if (!World->LineTraceSingleByChannel(Hit, P, P - FVector(0, 0, 500), ECC_Visibility, Query) || Hit.ImpactNormal.Z < .9 || FMath::Abs(Hit.ImpactPoint.Z - 2.5) > 10) ++Unsupported;
        }
        Test->TestEqual(TEXT("All 600 route samples have road collision"), Unsupported, 0);
        const auto& Route = Manifest->GetArrayField(TEXT("drivePath"));
        int32 FailedRejoins = 0;
        // Drive across both grass/road edges around the complete circuit, in
        // forward and reverse. This exercises swept body movement, not teleport
        // crossings or a centreline-only collision trace.
        for (int32 Index = 0; Index < Route.Num(); Index += 50)
        {
            const auto& A = Route[Index]->AsArray();
            const auto& B = Route[(Index + 1) % Route.Num()]->AsArray();
            const FVector Center(A[0]->AsNumber(), A[1]->AsNumber(), 18);
            const FVector Tangent = FVector(B[0]->AsNumber() - Center.X, B[1]->AsNumber() - Center.Y, 0).GetSafeNormal();
            const FVector Normal(-Tangent.Y, Tangent.X, 0);
            for (float Side : {-1.f, 1.f}) for (bool ReverseDrive : {false, true})
            {
                Kart->ResetKart();
                const FVector Offroad = Center + Normal * Side * 700;
                const FVector Inward = Normal * -Side;
                Kart->SetActorLocation(Offroad);
                Kart->SetActorRotation((ReverseDrive ? -Inward : Inward).Rotation());
                Kart->SetDriveInput(ReverseDrive ? -1 : 1, 0);
                for (int32 Frame = 0; Frame < 180; ++Frame) Kart->Tick(1.f / 60.f);
                if (FVector::DotProduct(Kart->GetActorLocation() - Offroad, Inward) < 650) ++FailedRejoins;
            }
        }
        Test->TestEqual(TEXT("48 driven grass-to-road rejoins succeed in forward and reverse"), FailedRejoins, 0);
        Race->RestartRace();
    }
    const auto Cross = [&](int32 Index, bool bForward = true)
    {
        const auto& Gate = Race->GetGates()[Index];
        const FVector Center = Gate.Transform.GetLocation();
        const FVector Offset = Gate.Transform.GetUnitAxis(EAxis::X) * 250;
        Kart->SetActorLocation(Center + (bForward ? -Offset : Offset)); Race->Tick(0);
        Kart->SetActorLocation(Center + (bForward ? Offset : -Offset)); Race->Tick(0);
    };
    Cross(0, false);
    Test->TestFalse(TEXT("Reverse crossing cannot start"), Race->GetProgress().bStarted);
    Cross(0); Cross(2); Cross(0);
    Test->TestEqual(TEXT("Skipping a gate cannot complete a lap"), Race->GetProgress().CompletedLaps, 0);
    for (int32 Lap = 0; Lap < 3; ++Lap)
    {
        for (int32 Gate = 1; Gate < 13; ++Gate) { Cross(Gate); Cross(Gate); }
        Cross(0);
    }
    Test->TestTrue(TEXT("Three ordered laps finish on the actual map"), Race->GetProgress().bFinished);
    const double Finished = Race->GetProgress().TotalTime(World->GetTimeSeconds());
    Test->TestEqual(TEXT("Finish freezes total time"), Race->GetProgress().TotalTime(World->GetTimeSeconds() + 60), Finished);
    Kart->SetDriveInput(1, 0); Kart->Tick(.1f);
    Race->RestartRace();
    Test->TestFalse(TEXT("Reset clears finish"), Race->GetProgress().bFinished);
    Test->TestTrue(TEXT("Reset returns kart to spawn"), Kart->GetActorLocation().Equals(Start, 2));
    Test->TestEqual(TEXT("Reset clears kart speed"), Kart->GetSpeedKmh(), 0.f);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartTrackPIETest, "RoadToF1.Kart.SouthGardaPIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FKartTrackPIETest::RunTest(const FString& Parameters)
{
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/RoadToF1/SouthGarda_KartRace")));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2));
    ADD_LATENT_AUTOMATION_COMMAND(FVerifyKartTrack(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}
#endif
