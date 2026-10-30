#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../KartNavigationMath.h"
#include "../KartNavigationMap.h"
#include "../TrackRacingAI.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNavigationProjectionTest,"RoadToF1.Navigation.ProjectionAndClipping",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FNavigationProjectionTest::RunTest(const FString&){
 using namespace KartNavigation;FView V;V.WorldCenter={2400,-1800};V.PixelOrigin={160,120};V.Pixels=FBox2D({0,0},{320,240});V.PixelsPerCm=.014;
 for(double Yaw:{0.,45.,90.,179.,-110.}){V.YawDegrees=Yaw;const FVector2D World(8400,-9200);TestTrue(TEXT("Rotated pan/zoom screen projection round trips"),V.Unproject(V.Project(World)).Equals(World,1.e-6));}
 V.WorldCenter=FVector2D::ZeroVector;V.YawDegrees=0;TestTrue(TEXT("World north is screen up"),V.Project({100,0}).Y<V.PixelOrigin.Y);TestTrue(TEXT("World east is screen right"),V.Project({0,100}).X>V.PixelOrigin.X);
 V.YawDegrees=90;TestTrue(TEXT("Heading-up east is ahead"),V.Project({0,100}).Y<V.PixelOrigin.Y);TestTrue(TEXT("North rotates left while driving east"),V.Project({100,0}).X<V.PixelOrigin.X);
 FVector2D A(-30,120),B(350,120);TestTrue(TEXT("Crossing road segment clips into viewport"),ClipLine(A,B,V.Pixels));TestTrue(TEXT("Clipped endpoints stay on frame"),A.Equals({0,120})&&B.Equals({320,120}));A={-20,-20};B={-10,200};TestFalse(TEXT("Completely outside road does not bleed over HUD"),ClipLine(A,B,V.Pixels));
 auto P=ClipPolygon({{-10,-10},{60,-10},{60,60},{-10,60}},FBox2D({0,0},{50,50}));TestEqual(TEXT("Clipped road face remains a quadrilateral"),P.Num(),4);for(auto Q:P)TestTrue(TEXT("No road polygon vertices escape the minimap"),Q.X>=0&&Q.X<=50&&Q.Y>=0&&Q.Y<=50);
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNavigationRouteTest,"RoadToF1.Navigation.ForwardWaypointRoute",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FNavigationRouteTest::RunTest(const FString&){
 using namespace KartNavigation;const TArray<FVector> Route={{0,0,0},{100,0,0},{100,100,0},{0,100,0}};
 const auto A=Nearest(Route,{70,-500});TestEqual(TEXT("Off-track click snaps to the nearest actual segment"),A.Segment,0);TestTrue(TEXT("Waypoint projects onto the segment interior"),A.Position.Equals({70,0},1.e-6));
 const auto B=Nearest(Route,{20,0});TestTrue(TEXT("Behind waypoint routes forward around the closed lap"),FMath::IsNearlyEqual(ForwardDistance(Route,A,B),350.,1.e-6));TestTrue(TEXT("Ahead waypoint follows only the remaining segment"),FMath::IsNearlyEqual(ForwardDistance(Route,B,A),50.,1.e-6));
 TestEqual(TEXT("Empty geometry cannot invent a waypoint"),Nearest({},{}).Segment,INDEX_NONE);
 const auto* Map=GetDefault<UKartNavigationMap>();const auto* Shared=GetDefault<UTrackRacingAI>()->RouteAsset.LoadSynchronous();TestTrue(TEXT("Navigation shares the existing AI edge data asset"),Map->GetRoute()==Shared&&Shared&&Shared->IsUsable());
 return true;
}
#endif
