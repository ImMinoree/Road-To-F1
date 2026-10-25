#include "KartSurfaceFX.h"
#include "ProofPawn.h"
#include "KartTireDynamics.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Materials/MaterialInterface.h"
#include "GameFramework/PlayerController.h"
#include "Camera/PlayerCameraManager.h"

UKartSurfaceFX::UKartSurfaceFX(){PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickGroup=TG_PostPhysics;SetIsReplicatedByDefault(false);}
EKartLooseSurface UKartSurfaceFX::ClassifyNames(const FString& Names){
 const FString S=Names.ToLower();
 if(S.Contains(TEXT("asphalt"))||S.Contains(TEXT("runoff"))||S.Contains(TEXT("curb"))||S.Contains(TEXT("kerb"))||S.Contains(TEXT("concrete"))||S.Contains(TEXT("surfaceasphalt")))return EKartLooseSurface::None;
 if(S.Contains(TEXT("grass"))||S.Contains(TEXT("lawn")))return EKartLooseSurface::Grass;
 if(S.Contains(TEXT("sand"))||S.Contains(TEXT("soil"))||S.Contains(TEXT("gravel"))||S.Contains(TEXT("surfacedirt")))return EKartLooseSurface::Dirt;
 return EKartLooseSurface::None;
}
void UKartSurfaceFX::BeginPlay(){
 Super::BeginPlay();
 if(!GetWorld()||GetWorld()->GetNetMode()==NM_DedicatedServer){SetComponentTickEnabled(false);return;}
 AddTickPrerequisiteActor(GetOwner());Random.Initialize(GetOwner()->GetUniqueID());
 const TCHAR* MeshNames[]={TEXT("SM_SoilChip"),TEXT("SM_GrassClipping"),TEXT("SM_DustQuad")};
 const TCHAR* MaterialNames[]={TEXT("M_SoilChip"),TEXT("M_GrassClipping"),TEXT("M_TireDust")};
 for(int32 Kind=0;Kind<3;++Kind){
  const FString Folder=TEXT("/Game/RoadToF1/SurfaceFX/");
  auto* Mesh=LoadObject<UStaticMesh>(nullptr,*(Folder+TEXT("Meshes/")+MeshNames[Kind]+TEXT(".")+MeshNames[Kind]));
  auto* Material=LoadObject<UMaterialInterface>(nullptr,*(Folder+TEXT("Materials/")+MaterialNames[Kind]+TEXT(".")+MaterialNames[Kind]));
  if(!Mesh||!Material){UE_LOG(LogTemp,Warning,TEXT("KART_SURFACE_FX: missing cosmetic assets; disabled safely"));SetComponentTickEnabled(false);return;}
  auto* C=NewObject<UInstancedStaticMeshComponent>(GetOwner(),NAME_None,RF_Transient);
  GetOwner()->AddInstanceComponent(C);C->SetupAttachment(GetOwner()->GetRootComponent());C->SetAbsolute(true,true,true);C->SetWorldTransform(FTransform::Identity);
  C->SetStaticMesh(Mesh);C->SetMaterial(0,Material);C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetGenerateOverlapEvents(false);C->SetCanEverAffectNavigation(false);C->SetCastShadow(false);C->SetVisibleInRayTracing(false);C->SetIsReplicated(false);C->NumCustomDataFloats=1;C->RegisterComponent();
  Pools.Add(C);
  for(int32 I=0;I<32;++I){FSpeck P;P.Kind=Kind;P.Index=I;Specks.Add(P);C->AddInstance(FTransform(FQuat::Identity,FVector::ZeroVector,FVector::ZeroVector));}
 }
 PreviousPosition=GetOwner()->GetActorLocation();PreviousYaw=GetOwner()->GetActorRotation().Yaw;bReady=true;
}
EKartLooseSurface UKartSurfaceFX::Probe(const FVector& Local,FVector& Contact) const{
 const FVector Foot=GetOwner()->GetActorTransform().TransformPosition(Local);
 FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(KartSurfaceFX),true,GetOwner());
 if(!GetWorld()->LineTraceSingleByChannel(Hit,Foot+FVector(0,0,50),Foot-FVector(0,0,35),ECC_Visibility,Q)||FMath::Abs(Hit.ImpactPoint.Z-Foot.Z)>18||Hit.ImpactNormal.Z<.5f)return EKartLooseSurface::None;
 Contact=Hit.ImpactPoint+Hit.ImpactNormal*2;
 FString Names;
 if(auto* C=Hit.GetComponent()){
  if(auto* S=Cast<UStaticMeshComponent>(C))if(S->GetStaticMesh())Names+=S->GetStaticMesh()->GetName();
  for(int32 I=0;I<C->GetNumMaterials();++I)if(auto* M=C->GetMaterial(I))Names+=TEXT(" ")+M->GetName();
  for(const FName& Tag:C->ComponentTags)Names+=TEXT(" ")+Tag.ToString();
 }
 if(auto* A=Hit.GetActor())for(const FName& Tag:A->Tags)Names+=TEXT(" ")+Tag.ToString();
 return ClassifyNames(Names);
}
void UKartSurfaceFX::Emit(int32 Kind,const FVector& Contact,const FVector& Motion,float Speed,float Side){
 const int32 Slot=Kind*32+(Cursor[Kind]++%32);auto& P=Specks[Slot];P.bLive=true;P.Age=0;P.Life=Kind==2?Random.FRandRange(.55f,.95f):Random.FRandRange(.35f,.7f);
 P.Position=Contact+FVector(Random.FRandRange(-4,4),Random.FRandRange(-4,4),2);
 P.Velocity=-Motion*Random.FRandRange(Speed*.12f,Speed*.28f)+GetOwner()->GetActorRightVector()*Random.FRandRange(-35,35)+FVector(0,0,Kind==2?Random.FRandRange(30,65):Random.FRandRange(75,155));
 P.Rotation=FRotator(Random.FRandRange(-180,180),Random.FRandRange(-180,180),Random.FRandRange(-180,180));P.Size=Kind==2?Random.FRandRange(11,20):Random.FRandRange(.55f,1.3f);++TotalEmitted;
}
void UKartSurfaceFX::Animate(float Dt){
 const float MotionDt=FMath::Min(Dt,.05f);
 FVector Eye=GetOwner()->GetActorLocation()+FVector(0,0,100);
 if(auto* PC=GetWorld()->GetFirstPlayerController())if(PC->PlayerCameraManager)Eye=PC->PlayerCameraManager->GetCameraLocation();
 LiveParticles=0;
 for(auto& P:Specks){
  if(!P.bLive)continue;P.Age+=Dt;
  if(P.Age>=P.Life){P.bLive=false;Pools[P.Kind]->UpdateInstanceTransform(P.Index,FTransform(FQuat::Identity,FVector::ZeroVector,FVector::ZeroVector),false,false,true);continue;}
  ++LiveParticles;const float T=P.Age/P.Life;
  P.Velocity.Z-=(P.Kind==2?15.f:460.f)*MotionDt;P.Position+=P.Velocity*MotionDt;
  float Size=P.Size;
  if(P.Kind==2){P.Velocity*=FMath::Exp(-2.1f*Dt);Size*=1+T*1.7f;P.Rotation=FRotationMatrix::MakeFromZ(Eye-P.Position).Rotator();Pools[2]->SetCustomDataValue(P.Index,0,(1-T)*(1-T),false);}
  else {P.Rotation.Yaw+=160*Dt;Size*=FMath::Min(1.f,(1-T)*5);}
  Pools[P.Kind]->UpdateInstanceTransform(P.Index,FTransform(P.Rotation,P.Position,FVector(Size)),false,false,true);
 }
 for(const auto& Pool:Pools)Pool->MarkRenderStateDirty();
}
void UKartSurfaceFX::TickComponent(float Dt,ELevelTick Type,FActorComponentTickFunction* Tick){
 Super::TickComponent(Dt,Type,Tick);if(!bReady||Dt<=SMALL_NUMBER)return;
 const FVector Position=GetOwner()->GetActorLocation(),Delta=Position-PreviousPosition;const float Yaw=GetOwner()->GetActorRotation().Yaw;
 const float Distance=Delta.Size2D(),Speed=Distance/Dt,Acceleration=FMath::Max(0.f,(Speed-PreviousSpeed)/Dt),Turn=FMath::Abs(FMath::FindDeltaAngleDegrees(PreviousYaw,Yaw))/Dt;
 PreviousPosition=Position;PreviousYaw=Yaw;PreviousSpeed=Speed;EmittingWheels=0;
 bool bNear=true;if(auto* PC=GetWorld()->GetFirstPlayerController())if(PC->PlayerCameraManager)bNear=FVector::DistSquared(Position,PC->PlayerCameraManager->GetCameraLocation())<FMath::Square(EffectDistanceCm);
 if(bEnabled&&bNear&&Speed>=MinimumSpeedCm&&Distance<FMath::Max(300.f,3500.f*Dt)){
  FVector Contacts[2];LeftSurface=Probe(RearLeft,Contacts[0]);RightSurface=Probe(RearRight,Contacts[1]);const EKartLooseSurface Surfaces[]={LeftSurface,RightSurface};
  for(int32 I=0;I<2;++I){
   if(Speed<MinimumSpeedCm||Surfaces[I]==EKartLooseSurface::None){Credits[I]=0;continue;}
   float Activity=1;
   if(const auto* Pawn=Cast<AProofPawn>(GetOwner()))if(Pawn->bUseTireDynamics)if(const auto* Dynamics=Pawn->GetTireDynamics()){
    const auto& Slip=Dynamics->Telemetry;
    Activity=Slip.GroundedWheels>0?FMath::Clamp(.15f+FMath::Abs(Slip.RearSlipDegrees)/15.f+FMath::Max(0.f,Slip.RearLongitudinalDemand-.5f)*.3f,0.f,1.f):0;
   }
   if(Activity<=0){Credits[I]=0;continue;}
   ++EmittingWheels;Credits[I]+=Dt*FMath::Clamp(5+Speed*.018f+FMath::Min(Acceleration,500.f)*.008f+FMath::Min(Turn,120.f)*.025f,5.f,34.f)*Activity;
   int32 Budget=0;while(Credits[I]>=1&&Budget++<4){Credits[I]-=1;Emit(Surfaces[I]==EKartLooseSurface::Grass&&Random.FRand()<.65f?1:0,Contacts[I],Delta.GetSafeNormal2D(),Speed,I?1:-1);if(Activity>.35f&&Random.FRand()<.32f*Activity)Emit(2,Contacts[I],Delta.GetSafeNormal2D(),Speed,I?1:-1);}
  }
 }else {Credits[0]=Credits[1]=0;LeftSurface=RightSurface=EKartLooseSurface::None;}
 Animate(Dt);
}
