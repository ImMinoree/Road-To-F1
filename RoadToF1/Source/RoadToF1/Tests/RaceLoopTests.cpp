#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "RaceProgress.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRaceRulesTest, "RoadToF1.RaceLoop.Rules", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRaceRulesTest::RunTest(const FString& Parameters)
{
    FRaceProgress Race;
    Race.Reset(3, 3);
    TestFalse(TEXT("Checkpoints cannot start race"), Race.CrossGate(1, 1));
    TestFalse(TEXT("Reverse crossing cannot start race"), Race.CrossGate(0, 2, false));
    TestTrue(TEXT("First crossing starts race"), Race.CrossGate(0, 10));
    TestEqual(TEXT("Starts on lap one"), Race.CurrentLap(), 1);
    TestFalse(TEXT("Back and forth at start cannot count a lap"), Race.CrossGate(0, 11));
    TestFalse(TEXT("Skipping CP1 is ignored"), Race.CrossGate(2, 12));
    TestFalse(TEXT("Invalid checkpoint ignored"), Race.CrossGate(4, 12));
    TestTrue(TEXT("CP1 accepted"), Race.CrossGate(1, 13));
    TestFalse(TEXT("Repeated CP1 ignored"), Race.CrossGate(1, 14));
    TestFalse(TEXT("Skipping CP2 is ignored"), Race.CrossGate(3, 15));
    TestFalse(TEXT("Incomplete lap cannot finish"), Race.CrossGate(0, 16));
    TestFalse(TEXT("Reverse CP2 ignored"), Race.CrossGate(2, 17, false));
    TestTrue(TEXT("CP2 accepted"), Race.CrossGate(2, 18));
    TestTrue(TEXT("CP3 accepted"), Race.CrossGate(3, 19));
    TestFalse(TEXT("Reverse finish cannot count even with all checkpoints"), Race.CrossGate(0, 20, false));
    TestTrue(TEXT("First complete lap accepted"), Race.CrossGate(0, 30));
    TestEqual(TEXT("Lap duration"), Race.LapTimes[0], 20.0);
    TestEqual(TEXT("Lap advances"), Race.CurrentLap(), 2);
    TestEqual(TEXT("Lap clock restarts"), Race.LapTime(35), 5.0);
    TestFalse(TEXT("Checkpoints must be earned again"), Race.CrossGate(0, 36));
    for (int32 Lap = 1; Lap < 3; ++Lap)
    {
        for (int32 CP = 1; CP <= 3; ++CP) TestTrue(TEXT("Ordered checkpoint accepted"), Race.CrossGate(CP, 30 + Lap * 20 + CP));
        TestTrue(TEXT("Complete lap accepted"), Race.CrossGate(0, 30 + Lap * 20 + 10));
    }
    TestTrue(TEXT("Target lap finishes race"), Race.bFinished);
    TestEqual(TEXT("Exactly three completed laps"), Race.CompletedLaps, 3);
    TestEqual(TEXT("Three lap records"), Race.LapTimes.Num(), 3);
    TestEqual(TEXT("Total time frozen"), Race.TotalTime(999), 70.0);
    TestEqual(TEXT("Final lap time frozen"), Race.LapTime(999), 20.0);
    TestFalse(TEXT("After-finish crossings ignored"), Race.CrossGate(0, 1000));
    Race.Reset(3, 3);
    TestFalse(TEXT("Reset returns to waiting"), Race.bStarted);
    TestFalse(TEXT("Reset clears finish"), Race.bFinished);
    TestEqual(TEXT("Reset clears laps"), Race.CompletedLaps, 0);
    TestEqual(TEXT("Reset clears checkpoints"), Race.NextCheckpoint, 0);
    TestEqual(TEXT("Reset clears lap records"), Race.LapTimes.Num(), 0);
    TestEqual(TEXT("Reset clears total time"), Race.TotalTime(1001), 0.0);
    TestTrue(TEXT("A second race can start"), Race.CrossGate(0, 1002));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRaceGateTest, "RoadToF1.RaceLoop.GateGeometry", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRaceGateTest::RunTest(const FString& Parameters)
{
    FRaceGateGeometry Gate;
    Gate.Transform = FTransform::Identity;
    double Fraction = 0;
    TestTrue(TEXT("Fast crossing cannot tunnel through gate"), Gate.ForwardCrossing(FVector(-2000, 0, 100), FVector(2000, 0, 100), Fraction));
    TestEqual(TEXT("Subframe crossing time"), Fraction, 0.5);
    TestFalse(TEXT("Reverse crossing rejected"), Gate.ForwardCrossing(FVector(100, 0, 100), FVector(-100, 0, 100), Fraction));
    TestFalse(TEXT("Remaining inside overlap does not retrigger"), Gate.ForwardCrossing(FVector(5, 0, 100), FVector(10, 0, 100), Fraction));
    TestFalse(TEXT("Driving beside gate rejected"), Gate.ForwardCrossing(FVector(-100, 1300, 100), FVector(100, 1300, 100), Fraction));
    TestFalse(TEXT("Flying above gate rejected"), Gate.ForwardCrossing(FVector(-100, 0, 500), FVector(100, 0, 500), Fraction));
    Gate.Transform = FTransform(FRotator(0, 90, 0), FVector(4500, 600, 20));
    TestTrue(TEXT("Rotated start line detected"), Gate.ForwardCrossing(FVector(4500, 500, 100), FVector(4500, 700, 100), Fraction));
    TestFalse(TEXT("Rotated start line reverse rejected"), Gate.ForwardCrossing(FVector(4500, 700, 100), FVector(4500, 500, 100), Fraction));
    return true;
}
#endif
