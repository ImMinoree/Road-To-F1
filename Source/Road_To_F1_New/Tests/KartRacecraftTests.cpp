#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../KartRacecraftMath.h"
#include "../TrackRacingAI.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartRacecraftTest,"RoadToF1.Racecraft.GapsAndDefense",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FKartRacecraftTest::RunTest(const FString&){
 using namespace KartRacecraft;
 TestTrue(TEXT("Lap wrap preserves nearby leader"),FMath::IsNearlyEqual(SignedGap(50,9950,10000),100.f));
 TestTrue(TEXT("Lap wrap preserves nearby pursuer"),FMath::IsNearlyEqual(SignedGap(9950,50,10000),-100.f));
 TestTrue(TEXT("Closing occupied lane is rejected"),Conflict(700,500,900,0,0));
 TestFalse(TEXT("Distinct parallel lane stays available"),Conflict(700,500,900,0,250));
 TestTrue(TEXT("Fast rear approach closes the gap"),Conflict(-800,1400,900,200,200));
 TestFalse(TEXT("Distant same lane need not be blocked"),Conflict(1800,900,900,0,0));
 TestFalse(TEXT("Never defend into an overlapping kart"),MayDefend(-500,true,0,.5));
 TestFalse(TEXT("Cooldown prevents weaving"),MayDefend(-500,false,2,.5));
 TestFalse(TEXT("No reactive late block"),MayDefend(-200,false,0,.5));
 TestTrue(TEXT("Early inside defense is allowed"),MayDefend(-900,false,0,.5));
 TestTrue(TEXT("Single rear-cleared blocked-route backoff permitted"),MayBackOff(true,false,0));
 TestFalse(TEXT("No blocked-route reversing loop"),MayBackOff(true,false,1));
 TestFalse(TEXT("Never reverse while alongside"),MayBackOff(false,true,0));
 const auto* AI=GetDefault<UTrackRacingAI>();TestEqual(TEXT("Nineteen requested opponents"),AI->OpponentCount,19);TestEqual(TEXT("Four configurable personalities"),AI->Drivers.Num(),4);
 return true;
}
#endif
