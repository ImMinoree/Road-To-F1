#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../KartRaceSettings.h"
#include "../KartTireModel.h"
#include "../TrackRacingAI.h"
#include "../KartTireDynamics.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTenKartDefaultsTest,"RoadToF1.Race.TenKartDefaultsAnd38Mph",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FTenKartDefaultsTest::RunTest(const FString&){
 TestEqual(TEXT("Nine opponents plus one player"),GetDefault<UTrackRacingAI>()->OpponentCount+1,KartRace::KartCount);
 TestEqual(TEXT("Player starts tenth"),KartRace::PlayerGridPosition,10);
 TestEqual(TEXT("All spawned karts inherit 38mph ceiling"),GetDefault<UKartTireDynamics>()->MaximumForwardSpeedMph,38.f);
 KartDynamics::Parameters P;KartDynamics::State S;KartDynamics::Contact C;KartDynamics::Input I;I.Throttle=1;double Peak=0;
 for(int N=0;N<240*25;++N){KartDynamics::Step(S,P,C,I,KartDynamics::StepSeconds);Peak=FMath::Max(Peak,S.U);}
 TestTrue(TEXT("Straight acceleration reaches 38mph"),FMath::Abs(S.U-KartRace::TopSpeedMps)<.01);
 TestTrue(TEXT("Forward governor does not exceed 38mph"),Peak<=KartRace::TopSpeedMps+1.e-6);
 I.Throttle=0;I.Brake=1;for(int N=0;N<240*8;++N)KartDynamics::Step(S,P,C,I,KartDynamics::StepSeconds);
 TestTrue(TEXT("Existing brakes still stop the faster kart"),FMath::Abs(S.U)<.05);
 return true;
}
#endif

