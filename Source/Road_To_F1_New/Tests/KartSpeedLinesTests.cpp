#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../KartSpeedLinesMath.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartSpeedLinesTest,"RoadToF1.SpeedLines.SpeedResponse",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FKartSpeedLinesTest::RunTest(const FString&){
 using namespace KartSpeedLines;
 TestEqual(TEXT("Stopped"),Strength(0),0.f);TestEqual(TEXT("Threshold remains clear"),Strength(19),0.f);
 TestTrue(TEXT("Subtle at 25 actual km/h"),Strength(25)>0&&Strength(25)<.15f);
 TestTrue(TEXT("Noticeable at 40 actual km/h"),Strength(40)>.15f&&Strength(40)<.6f);
 TestTrue(TEXT("Strong at 55 actual km/h"),Strength(55)>.6f);TestEqual(TEXT("Full animation at 61 actual km/h"),Strength(61),1.f);
 float A=0,B=0;for(int I=0;I<30;++I)A=Smooth(A,1,1.f/30);for(int I=0;I<120;++I)B=Smooth(B,1,1.f/120);
 TestTrue(TEXT("Frame-rate independent response"),FMath::IsNearlyEqual(A,B,1.e-5f));
 float Previous=0;for(int I=0;I<=1200;++I){float V=Strength(I*.1f);TestTrue(TEXT("Monotonic finite bounded response"),FMath::IsFinite(V)&&V>=Previous&&V<=1);Previous=V;}
 return true;
}
#endif
