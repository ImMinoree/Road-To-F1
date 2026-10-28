#include "KartTireDynamics.h"
#include "ProofPawn.h"
#include "Components/PrimitiveComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/AudioComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Materials/MaterialInterface.h"
#include "PhysicalMaterials/PhysicalMaterial.h"
#include "Sound/SoundBase.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"

UKartTireDynamics::UKartTireDynamics(){PrimaryComponentTick.bCanEverTick=false;SetIsReplicatedByDefault(false);}
KartDynamics::Parameters UKartTireDynamics::Parameters()const{
 KartDynamics::Parameters P;
 P.Mass=FMath::Clamp(MassKg,80.f,300.f);P.Inertia=FMath::Clamp(YawInertiaKgM2,25.f,200.f);
 P.Wheelbase=FMath::Clamp(WheelbaseM,.8f,1.5f);P.FrontDistance=FMath::Clamp(double(CGToFrontAxleM),P.Wheelbase*.3,P.Wheelbase*.7);
 P.Track=FMath::Clamp(TrackWidthM,.8f,1.5f);P.CGHeight=FMath::Clamp(CGHeightM,.1f,.45f);
 P.FrontStiffness=FMath::Clamp(FrontCorneringStiffness,2000.f,30000.f);P.RearStiffness=FMath::Clamp(RearCorneringStiffness,2000.f,30000.f);
 P.RearGripScale=FMath::Clamp(RearGripScale,.8f,1.3f);P.SlidingDrop=FMath::Clamp(SlidingGripDrop,0.f,.25f);
 P.RearLateralGripReserve=FMath::Clamp(RearLateralGripReserve,0.f,.95f);
 P.RelaxationLength=FMath::Clamp(RelaxationLengthM,.05f,.4f);P.AxleScrub=FMath::Clamp(RearAxleScrub,0.f,30.f);
 P.EngineForce=FMath::Clamp(EngineForceN,100.f,1500.f);P.BrakeForce=FMath::Clamp(BrakeForceN,100.f,1800.f);P.RearBrakeBias=FMath::Clamp(RearBrakeBias,0.f,1.f);
 P.LinearDrag=FMath::Clamp(LinearDragPerSecond,.05f,1.f);P.RollingForce=FMath::Clamp(RollingResistanceN,0.f,50.f);
 P.MaximumForwardSpeed=FMath::Clamp(MaximumForwardSpeedMph,1.f,100.f)*.44704;
 P.MaxSteerDegrees=FMath::Clamp(MaximumSteeringDegrees,10.f,30.f);P.SteerRate=FMath::Clamp(SteeringRateRadPerSecond,1.f,6.f);P.HighSpeedSteerReduction=FMath::Clamp(HighSpeedSteeringReduction,0.f,1.f);
 P.SteeringLateralAccelerationG=FMath::Clamp(SteeringLateralAccelerationG,0.f,1.5f);
 P.SteeringResponseSeconds=FMath::Clamp(SteeringResponseSeconds,0.f,.5f);
 P.DriftEnterDegrees=FMath::Clamp(DriftEnterDegrees,3.f,20.f);P.DriftExitDegrees=FMath::Clamp(double(DriftExitDegrees),1.0,P.DriftEnterDegrees-1);
 P.DriftMinSpeed=FMath::Clamp(DriftMinimumSpeedMps,2.f,6.f);P.DriftHold=FMath::Clamp(DriftSustainSeconds,.05f,.5f);P.RecoveryHold=FMath::Clamp(GripRecoverySeconds,.05f,.5f);
 return P;
}
void UKartTireDynamics::BeginPlay(){
 Super::BeginPlay();ResetMotion();
 bLogTelemetry=bLogTelemetry||FParse::Param(FCommandLine::Get(),TEXT("KartTelemetry"));
 if(bLogTelemetry){
  const FString Dir=FPaths::ProjectDir()/TEXT("Evidence/TireDynamics");IFileManager::Get().MakeDirectory(*Dir,true);
  LogPath=Dir/(FString(TEXT("drive_"))+GetOwner()->GetName()+TEXT(".csv"));
  FFileHelper::SaveStringToFile(TEXT("time,u_mps,v_mps,beta_deg,yaw_deg_s,front_slip_deg,rear_slip_deg,front_fx_n,rear_fx_n,front_fy_n,rear_fy_n,front_use,rear_use,front_mu,rear_mu,steer_deg,drifting,grounded,z_cm,collisions,steps,dropped_seconds,contact_impulse_ns,max_penetration_cm,vertical_accel_g\n"),*LogPath);
 }
 if(!TireScrubSound.IsNull()&&GetWorld()->GetNetMode()!=NM_DedicatedServer)if(auto* Sound=TireScrubSound.LoadSynchronous()){
  ScrubAudio=NewObject<UAudioComponent>(GetOwner());GetOwner()->AddInstanceComponent(ScrubAudio);ScrubAudio->SetupAttachment(GetOwner()->GetRootComponent());ScrubAudio->SetSound(Sound);ScrubAudio->bAutoActivate=false;ScrubAudio->RegisterComponent();
 }
}
void UKartTireDynamics::EndPlay(const EEndPlayReason::Type Reason){
 if(!LogPath.IsEmpty()&&!LogRows.IsEmpty())FFileHelper::SaveStringToFile(LogRows,*LogPath,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);
 if(ScrubAudio)ScrubAudio->DestroyComponent();Super::EndPlay(Reason);
}
void UKartTireDynamics::ResetMotion(){
 State=KartDynamics::State();Accumulator=VerticalSpeed=0;Telemetry=FKartSlipTelemetry();GroundNormal=FVector::UpVector;
 LastContactImpulseNs=MaximumContactImpulseNs=MaximumPenetrationCm=VerticalAccelerationG=0;
 if(GetOwner()){const FVector Pos=GetOwner()->GetActorLocation();State.X=Pos.X*.01;State.Y=Pos.Y*.01;State.Heading=FMath::DegreesToRadians(GetOwner()->GetActorRotation().Yaw);}
 if(ScrubAudio)ScrubAudio->Stop();
}
EKartGripSurface UKartTireDynamics::ClassifySurface(const FString& Names){
 const FString S=Names.ToLower();
 if(S.Contains(TEXT("curb"))||S.Contains(TEXT("kerb")))return EKartGripSurface::Curb;
 if(S.Contains(TEXT("asphalt"))||S.Contains(TEXT("runoff"))||S.Contains(TEXT("concrete")))return EKartGripSurface::Asphalt;
 if(S.Contains(TEXT("grass"))||S.Contains(TEXT("lawn")))return EKartGripSurface::Grass;
 if(S.Contains(TEXT("dirt"))||S.Contains(TEXT("sand"))||S.Contains(TEXT("soil"))||S.Contains(TEXT("gravel")))return EKartGripSurface::Dirt;
 return EKartGripSurface::Unknown;
}
void UKartTireDynamics::ProbeGround(){
 const auto P=Parameters();const FVector Center=GetOwner()->GetActorLocation();
 FCollisionQueryParams Q(SCENE_QUERY_STAT(KartTireGround),true,GetOwner());Q.bReturnPhysicalMaterial=true;Q.bReturnFaceIndex=true;
 FCollisionObjectQueryParams Objects;Objects.AddObjectTypesToQuery(ECC_WorldStatic);Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
 double Mu[2]={0,0},Supports[2]={0,0};EKartGripSurface Types[2]={EKartGripSurface::Airborne,EKartGripSurface::Airborne};
 bHasGround=false;GroundHeight=0;GroundNormal=FVector::ZeroVector;Telemetry.GroundedWheels=0;
 double Heights[2]={0,0},SideHeight[2]={0,0},SideCount[2]={0,0};
 for(int32 I=0;I<4;++I){const int32 Axle=I/2;
  const FVector Local((Axle==0?P.FrontDistance:-(P.Wheelbase-P.FrontDistance))*100,(I%2?1:-1)*P.Track*50,0);
  const FVector Foot=GetOwner()->GetActorTransform().TransformPosition(Local);FHitResult Hit;
  if(!GetWorld()->LineTraceSingleByObjectType(Hit,Foot+FVector(0,0,12),Foot-FVector(0,0,85),Objects,Q)||Hit.ImpactNormal.Z<.55||FMath::Abs(Hit.ImpactPoint.Z+31-Center.Z)>25)continue;
  FString Names,Tags,MeshName;
  if(auto* C=Hit.GetComponent()){
   if(auto* Mesh=Cast<UStaticMeshComponent>(C))if(Mesh->GetStaticMesh())MeshName=Mesh->GetStaticMesh()->GetName();
   int32 Section=INDEX_NONE;
   if(auto* Material=C->GetMaterialFromCollisionFaceIndex(Hit.FaceIndex,Section))Names+=Material->GetName();
   else if(C->GetNumMaterials()==1)if(auto* FallbackMaterial=C->GetMaterial(0))Names+=FallbackMaterial->GetName();
   for(auto Tag:C->ComponentTags)Tags+=TEXT(" ")+Tag.ToString();
  }
  if(auto* Actor=Hit.GetActor())for(auto Tag:Actor->Tags)Tags+=TEXT(" ")+Tag.ToString();
  if(Hit.PhysMaterial.IsValid())Names+=TEXT(" ")+Hit.PhysMaterial->GetName();
  auto Surface=ClassifySurface(Tags);
  if(Surface==EKartGripSurface::Unknown)Surface=ClassifySurface(Names);
  if(Surface==EKartGripSurface::Unknown)Surface=ClassifySurface(MeshName);
  float Grip=AsphaltGrip;
  switch(Surface){case EKartGripSurface::Curb:Grip=CurbGrip;break;case EKartGripSurface::Grass:Grip=GrassGrip;break;case EKartGripSurface::Dirt:Grip=DirtGrip;break;default:break;}
  // Honor explicitly authored physical materials. The engine's unassigned default is not a surface assignment.
  if(Hit.PhysMaterial.IsValid()&&!Hit.PhysMaterial->GetPathName().StartsWith(TEXT("/Engine/EngineMaterials/DefaultPhysicalMaterial")))Grip=Hit.PhysMaterial->Friction;
  Mu[Axle]+=FMath::Clamp(Grip,.1f,2.f);Supports[Axle]+=1;Types[Axle]=Surface;
  GroundHeight+=float(Hit.ImpactPoint.Z);GroundNormal+=Hit.ImpactNormal;Heights[Axle]+=Hit.ImpactPoint.Z;
  SideHeight[I%2]+=Hit.ImpactPoint.Z;++SideCount[I%2];++Telemetry.GroundedWheels;
 }
 Contact.FrontMu=Supports[0]>0?Mu[0]/Supports[0]:AsphaltGrip;Contact.RearMu=Supports[1]>0?Mu[1]/Supports[1]:AsphaltGrip;
 Contact.FrontSupport=Supports[0]*.5;Contact.RearSupport=Supports[1]*.5;
 bHasGround=Telemetry.GroundedWheels>=2;Telemetry.FrontSurface=Types[0];Telemetry.RearSurface=Types[1];
 if(Telemetry.GroundedWheels>0){GroundHeight/=Telemetry.GroundedWheels;GroundNormal.Normalize();}
 else GroundNormal=FVector::UpVector;
 // Wheel-height fit also describes a kerb transition where individual face normals are flat.
 if(Supports[0]>0&&Supports[1]>0&&SideCount[0]>0&&SideCount[1]>0){
  const FVector LocalNormal(-(Heights[0]/Supports[0]-Heights[1]/Supports[1])/(P.Wheelbase*100),
   -(SideHeight[1]/SideCount[1]-SideHeight[0]/SideCount[0])/(P.Track*100),1);
  GroundNormal=FRotator(0,GetOwner()->GetActorRotation().Yaw,0).RotateVector(LocalNormal.GetSafeNormal());
 }
}
void UKartTireDynamics::ResolveHit(const FHitResult& Hit){
 if(Hit.ImpactNormal.Z>.55){if(VerticalSpeed<0)VerticalSpeed=0;return;}
 ++CollisionCount;MaximumPenetrationCm=FMath::Max(MaximumPenetrationCm,Hit.PenetrationDepth);
 auto* OtherPawn=Cast<AProofPawn>(Hit.GetActor());
 auto* Other=OtherPawn&&OtherPawn->bUseTireDynamics?OtherPawn->GetTireDynamics():nullptr;
 const FVector Position=GetOwner()->GetActorLocation(),OtherPosition=Other?Other->GetOwner()->GetActorLocation():FVector::ZeroVector;
 FVector Point=Hit.ImpactPoint;
 if(Other)Point=(Position+OtherPosition)*.5;
 else {
  // A box sweep may return an arbitrary face vertex. Use the closest face location to
  // avoid inventing a large yaw torque on a centered impact against a broad flat wall.
  FVector Closest;const auto* Component=Hit.GetComponent();
  if(Component&&Component->GetClosestPointOnCollision(Position,Closest)>=0)Point=Closest;
  else Point=Position+Hit.Normal*FVector::DotProduct(Hit.ImpactPoint-Position,Hit.Normal);
 }
 const auto P=Parameters();const auto OP=Other?Other->Parameters():KartDynamics::Parameters();
 const double J=KartDynamics::ResolveContact(State,P,Other?&Other->State:nullptr,Other?&OP:nullptr,
  Position.X*.01,Position.Y*.01,OtherPosition.X*.01,OtherPosition.Y*.01,Point.X*.01,Point.Y*.01,Hit.Normal.X,Hit.Normal.Y,
  FMath::Clamp(ContactFriction,0.f,1.f),FMath::Clamp(ContactRestitution,0.f,.2f));
 LastContactImpulseNs=FMath::Max(LastContactImpulseNs,float(J));MaximumContactImpulseNs=FMath::Max(MaximumContactImpulseNs,float(J));
 if(Other){Other->LastContactImpulseNs=FMath::Max(Other->LastContactImpulseNs,float(J));Other->MaximumContactImpulseNs=FMath::Max(Other->MaximumContactImpulseNs,float(J));Other->Publish();}
 if(Hit.bStartPenetrating){
  // Bounded query-based depenetration only; never discard all physical motion.
  FHitResult Correction;GetOwner()->AddActorWorldOffset(Hit.Normal*FMath::Min(Hit.PenetrationDepth+.125f,2.f),true,&Correction);
 }
}
void UKartTireDynamics::HoldForStart(float Dt,float Steering){
 State.ClearMotion();Accumulator=VerticalSpeed=0;
 KartDynamics::UpdateSteering(State,Parameters(),Steering,FMath::Clamp(Dt,0.f,.1f));ProbeGround();Publish();WriteLog(Dt);
 if(ScrubAudio)ScrubAudio->Stop();
}
FVector UKartTireDynamics::GetWorldVelocity()const{
 const double Co=std::cos(State.Heading),Si=std::sin(State.Heading);
 return FVector((Co*State.U-Si*State.V)*100,(Si*State.U+Co*State.V)*100,VerticalSpeed*100);
}
float UKartTireDynamics::GetMaximumCurvatureCm()const{const auto P=Parameters();return float(std::tan(KartDynamics::MaxSteer(P,std::abs(State.U)))/P.Wheelbase*.01);}
float UKartTireDynamics::SteeringForCurvature(float K)const{
 const auto P=Parameters();const double Desired=std::atan(double(K)*100*P.Wheelbase);
 // Input feedback, not applied yaw/velocity: damp a developing rear slide for autonomous drivers.
 return FMath::Clamp(float((Desired+State.Beta*.5-State.R*.015)/KartDynamics::MaxSteer(P,std::abs(State.U))),-1.f,1.f);
}
void UKartTireDynamics::Simulate(float Dt,float Throttle,float Steering,bool bBrake){
 if(!GetWorld()||!GetOwner()||!FMath::IsFinite(Dt)||Dt<=0)return;
 const auto P=Parameters();const double Accepted=FMath::Min(double(Dt),.25);DroppedSimulationSeconds+=float(Dt-Accepted);Accumulator+=Accepted;
 ProbeGround();int32 Count=0;LastContactImpulseNs*=FMath::Exp(-20.f*float(Accepted));
 const KartDynamics::Input Input{FMath::Clamp(double(Throttle),-1.0,1.0),FMath::Clamp(double(Steering),-1.0,1.0),bBrake?1.0:0.0};
 while(Accumulator+1e-9>=KartDynamics::StepSeconds&&Count++<60){
  const FVector Before=GetOwner()->GetActorLocation();State.X=Before.X*.01;State.Y=Before.Y*.01;State.Heading=FMath::DegreesToRadians(GetOwner()->GetActorRotation().Yaw);
  KartDynamics::Step(State,P,Contact,Input);++StepCount;
  const FVector Forward(FMath::Cos(State.Heading),FMath::Sin(State.Heading),0);
  const FQuat Target=FRotationMatrix::MakeFromXZ(Forward,bHasGround?GroundNormal:FVector::UpVector).ToQuat();
  // Surface attitude is a damped support approximation; yaw still comes exclusively from tire/contact torque.
  FRotator Pose=FQuat::Slerp(GetOwner()->GetActorQuat(),Target,1-FMath::Exp(-18*float(KartDynamics::StepSeconds))).Rotator();Pose.Yaw=KartDynamics::Deg(State.Heading);
  GetOwner()->SetActorRotation(Pose);
  FVector Delta(State.X*100-Before.X,State.Y*100-Before.Y,0);
  const double W=FMath::Clamp(GroundResponseRadPerSecond,10.f,40.f);
  const double Support=bHasGround?FMath::Max(0.0,KartDynamics::Gravity+W*W*(GroundHeight+31-Before.Z)*.01-2*W*VerticalSpeed):0;
  const double AZ=Support-KartDynamics::Gravity;VerticalAccelerationG=AZ/KartDynamics::Gravity;
  VerticalSpeed+=AZ*KartDynamics::StepSeconds;Delta.Z=VerticalSpeed*100*KartDynamics::StepSeconds;
  double Remaining=KartDynamics::StepSeconds;
  for(int32 ContactIndex=0;ContactIndex<3;++ContactIndex){
   FHitResult Hit;GetOwner()->AddActorWorldOffset(Delta,true,&Hit);
   if(!Hit.bBlockingHit)break;
   ResolveHit(Hit);Remaining*=1-Hit.Time;
   // Recompute from post-impact momentum; an old pre-impact delta can tunnel or cancel momentum twice.
   Delta=FVector::VectorPlaneProject(GetWorldVelocity()*Remaining,Hit.Normal);
   if(Delta.IsNearlyZero(.001))break;
  }
  Accumulator-=KartDynamics::StepSeconds;
  if(Count%4==0)ProbeGround();
 }
 Publish();WriteLog(Dt);
 if(ScrubAudio){
  const float Severity=Telemetry.GroundedWheels>0?FMath::Clamp((FMath::Abs(Telemetry.RearSlipDegrees)-3.f)/12.f,0.f,1.f)*FMath::Clamp(float(std::hypot(State.U,State.V))/5.f,0.f,1.f):0;
  ScrubAudio->SetVolumeMultiplier(Severity*.25f);ScrubAudio->SetPitchMultiplier(.95f+Severity*.15f);
  if(Severity>.05f&&!ScrubAudio->IsPlaying())ScrubAudio->Play();else if(Severity<=.01f&&ScrubAudio->IsPlaying())ScrubAudio->Stop();
 }
}
void UKartTireDynamics::Publish(){
 Telemetry.LongitudinalSpeedMps=State.U;Telemetry.LateralSpeedMps=State.V;Telemetry.SideslipDegrees=KartDynamics::Deg(State.Beta);Telemetry.YawRateDegrees=KartDynamics::Deg(State.R);
 Telemetry.FrontSlipDegrees=KartDynamics::Deg(State.FrontAlpha);Telemetry.RearSlipDegrees=KartDynamics::Deg(State.RearAlpha);Telemetry.SteeringDegrees=KartDynamics::Deg(State.Steer);
 Telemetry.FrontLateralForceN=State.FrontFy;Telemetry.RearLateralForceN=State.RearFy;Telemetry.FrontLongitudinalForceN=State.FrontFx;Telemetry.RearLongitudinalForceN=State.RearFx;
 Telemetry.FrontSaturation=State.FrontUtilization;Telemetry.RearSaturation=State.RearUtilization;Telemetry.RearLongitudinalDemand=State.RearLongDemand;
 Telemetry.FrontGrip=Contact.FrontMu;Telemetry.RearGrip=Contact.RearMu;Telemetry.LateralAccelerationG=State.Ay/KartDynamics::Gravity;
 Telemetry.RearInsideLoadFraction=State.RearInsideFraction;Telemetry.bDrifting=State.Drifting;Telemetry.bOversteering=State.Oversteering;
}
void UKartTireDynamics::WriteLog(float Dt){
 if(LogPath.IsEmpty())return;LogClock+=Dt;FlushClock+=Dt;
 if(LogClock>=.05){LogClock=0;LogRows+=FString::Printf(TEXT("%.4f,%.5f,%.5f,%.4f,%.4f,%.4f,%.4f,%.3f,%.3f,%.3f,%.3f,%.5f,%.5f,%.3f,%.3f,%.4f,%d,%d,%.3f,%d,%d,%.4f,%.3f,%.3f,%.4f\n"),GetWorld()->GetTimeSeconds(),State.U,State.V,KartDynamics::Deg(State.Beta),KartDynamics::Deg(State.R),KartDynamics::Deg(State.FrontAlpha),KartDynamics::Deg(State.RearAlpha),State.FrontFx,State.RearFx,State.FrontFy,State.RearFy,State.FrontUtilization,State.RearUtilization,Contact.FrontMu,Contact.RearMu,KartDynamics::Deg(State.Steer),State.Drifting?1:0,Telemetry.GroundedWheels,GetOwner()->GetActorLocation().Z,CollisionCount,StepCount,DroppedSimulationSeconds,LastContactImpulseNs,MaximumPenetrationCm,VerticalAccelerationG);}
 if(FlushClock>=1&&!LogRows.IsEmpty()){FFileHelper::SaveStringToFile(LogRows,*LogPath,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);LogRows.Empty();FlushClock=0;}
}
