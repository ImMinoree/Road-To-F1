#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "Tests/AutomationEditorCommon.h"
#include "Tests/AutomationCommon.h"
#include "RaceLoopSubsystem.h"
#include "RaceLoopWidget.h"
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Components/PrimitiveComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FVerifyRoadToF1Race, FAutomationTestBase*, Test);
bool FVerifyRoadToF1Race::Update()
{
    UWorld* World = AutomationCommon::GetAnyGameWorld();
    if (!World) { Test->AddError(TEXT("PIE world missing")); return true; }
    URaceLoopSubsystem* Race = World->GetSubsystem<URaceLoopSubsystem>();
    APawn* Pawn = UGameplayStatics::GetPlayerPawn(World, 0);
    if (!Race || !Pawn) { Test->AddError(TEXT("Race subsystem or vehicle missing")); return true; }
    Race->Tick(0);
    Test->TestTrue(TEXT("Saved prototype discovers existing trigger"), Race->IsRaceAvailable());
    if (!Race->IsRaceAvailable()) return true;
    Test->TestEqual(TEXT("Saved track has start plus three checkpoints"), Race->GetGates().Num(), 4);
    TArray<UUserWidget*> Widgets;
    UWidgetBlueprintLibrary::GetAllWidgetsOfClass(World, Widgets, URaceLoopWidget::StaticClass(), false);
    Test->TestEqual(TEXT("Race HUD created in PIE"), Widgets.Num(), 1);
    UPrimitiveComponent* Body = Cast<UPrimitiveComponent>(Pawn->GetRootComponent());
    const bool bWasSimulating = Body && Body->IsSimulatingPhysics();
    if (Body) Body->SetSimulatePhysics(false);
    const auto Cross = [&](int32 GateIndex, bool bForward = true)
    {
        const FRaceGateGeometry& Gate = Race->GetGates()[GateIndex];
        const FVector Offset = Gate.Transform.GetUnitAxis(EAxis::X) * 250;
        const FVector Center = Gate.Transform.GetLocation() + FVector(0, 0, 80);
        Pawn->SetActorLocation(Center + (bForward ? -Offset : Offset), false, nullptr, ETeleportType::TeleportPhysics);
        Race->Tick(0);
        Pawn->SetActorLocation(Center + (bForward ? Offset : -Offset), false, nullptr, ETeleportType::TeleportPhysics);
        Race->Tick(0);
    };
    Race->RestartRace();
    Cross(0, false);
    Test->TestFalse(TEXT("Reversing cannot start race in PIE"), Race->GetProgress().bStarted);
    Cross(0);
    Test->TestTrue(TEXT("Driving forward starts lap one in PIE"), Race->GetProgress().bStarted);
    Cross(0, false);
    Cross(0);
    Test->TestEqual(TEXT("Repeated start-line crossings do not count laps"), Race->GetProgress().CompletedLaps, 0);
    Cross(2);
    Test->TestEqual(TEXT("Skipped checkpoint ignored in PIE"), Race->GetProgress().NextCheckpoint, 0);
    Cross(1);
    Cross(1);
    Test->TestEqual(TEXT("Repeated checkpoint ignored in PIE"), Race->GetProgress().NextCheckpoint, 1);
    Cross(2);
    Cross(3);
    Cross(0, false);
    Test->TestEqual(TEXT("Reverse finish ignored with all checkpoints in PIE"), Race->GetProgress().CompletedLaps, 0);
    Cross(0);
    Test->TestEqual(TEXT("Ordered circuit completes first lap in PIE"), Race->GetProgress().CompletedLaps, 1);
    for (int32 Lap = 1; Lap < 3; ++Lap) { Cross(1); Cross(2); Cross(3); Cross(0); }
    Test->TestTrue(TEXT("Three laps finish race in PIE"), Race->GetProgress().bFinished);
    const double FinalTotal = Race->GetProgress().TotalTime(World->GetTimeSeconds());
    Test->TestEqual(TEXT("Final timer stays frozen"), Race->GetProgress().TotalTime(World->GetTimeSeconds() + 100), FinalTotal);
    Race->RestartRace();
    Test->TestFalse(TEXT("Restart clears finish state in PIE"), Race->GetProgress().bFinished);
    Test->TestEqual(TEXT("Restart clears lap history in PIE"), Race->GetProgress().LapTimes.Num(), 0);
    Test->TestTrue(TEXT("Restart returns vehicle to its start"), Pawn->GetActorLocation().Equals(FVector(4450, 0, 102), 2));
    Cross(0);
    Test->TestTrue(TEXT("Second race starts after reset in PIE"), Race->GetProgress().bStarted);
    Race->RestartRace();
    if (Body) Body->SetSimulatePhysics(bWasSimulating);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRacePIETest, "RoadToF1.RaceLoop.PrototypePIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRacePIETest::RunTest(const FString& Parameters)
{
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/RoadToF1/RacePrototype")));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2));
    ADD_LATENT_AUTOMATION_COMMAND(FVerifyRoadToF1Race(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}
#endif
