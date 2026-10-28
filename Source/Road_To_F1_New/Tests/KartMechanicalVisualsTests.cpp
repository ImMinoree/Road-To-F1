#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../KartVisualKinematics.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartLinkageTest,"RoadToF1.PlayerVehicleV4.FixedRodSteering",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FKartLinkageTest::RunTest(const FString&){
 for(int I=-240;I<=240;++I){
  const float Angle=I*.1f;const auto S=KartVisual::Solve(Angle);
  if(FMath::Abs(Angle)>1.f)TestTrue(TEXT("Cockpit wheel turns with the front tires from the driver view"),KartVisual::SteeringWheelDegrees(S.Column)*Angle<0.f);
  TestTrue(TEXT("Mean visual angle follows authoritative bicycle angle"),FMath::Abs((S.Left+S.Right)*.5f-Angle)<.01f);
  for(int Side:{-1,1})TestTrue(TEXT("Fixed rods remain attached through both locks"),FMath::Abs(FVector::Dist(KartVisual::Pin(S.Column),KartVisual::Pickup(Side,Side<0?S.Left:S.Right))-KartVisual::RodLength(Side))<.002f);
  if(Angle>1)TestTrue(TEXT("Inside right wheel turns farther"),S.Right>S.Left);
  if(Angle<-1)TestTrue(TEXT("Inside left wheel turns farther"),S.Left<S.Right);
  TestTrue(TEXT("Fixed-grip column stays inside baked reach"),FMath::Abs(S.Column)<45);
 }
 return true;
}
#endif
