#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../KartRaceAwarenessMath.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartAwarenessTest,"RoadToF1.RaceAwareness.RelativeMotion",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FKartAwarenessTest::RunTest(const FString&){
 using namespace KartAwareness;
 TestEqual(TEXT("Left overlap"),Risk({0,-190,0},{0,0,0},100),2);
 TestEqual(TEXT("Right overlap"),Risk({0,190,0},{0,0,0},100),2);
 TestEqual(TEXT("Stationary rear kart stays informational"),Risk({-800,0,0},{0,0,0},800),0);
 TestEqual(TEXT("Rear kart approaching rapidly"),Risk({-800,0,0},{1200,0,0},800),2);
 TestEqual(TEXT("Gradual approach"),Risk({-1200,0,0},{1000,0,0},1200),1);
 TestEqual(TEXT("Receding is not a closing alert"),Risk({-800,0,0},{-1200,0,0},800),0);
 TestEqual(TEXT("Other track branch filtered"),Risk({0,700,0},{0,0,0},12000),-1);
 TestEqual(TEXT("Immediate collision bypasses route ambiguity"),Risk({0,190,0},{0,0,0},12000),2);
 TestEqual(TEXT("Different elevation filtered"),Risk({0,190,500},{0,0,0},100),-1);
 TestEqual(TEXT("Out of range"),Risk({3000,0,0},{0,0,0},3000),-1);
 return true;
}
#endif
