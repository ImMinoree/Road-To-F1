#include "../Source/Road_To_F1_New/KartTireModel.h"
#include <cstdio>
#include <cstring>
using namespace KartDynamics;
struct Metrics {double MaxBeta=0,MaxRear=0,MaxFront=0,MaxYaw=0,MaxSpeed=0,EndSpeed=0,EndBeta=0,EndYaw=0,MinMu=2;int DriftFrames=0;bool Finite=true;};
Metrics Run(const char* Name,int Case,const char* Path=nullptr,double Brake=1,double Steering=.12,double Initial=11){
 Parameters P;State S;Contact C;Input I;Metrics M;
 if(Case>=2&&Case<=6)S.U=Initial;
 FILE* File=Path?std::fopen(Path,"w"):nullptr;
 if(File)std::fprintf(File,"t,u_mps,v_mps,beta_deg,yaw_deg_s,front_slip_deg,rear_slip_deg,front_fx_n,rear_fx_n,front_fy_n,rear_fy_n,front_use,rear_use,mu,steer_deg,drifting\n");
 const double Duration=Case==0?13:10;
 for(int K=0;K<int(Duration/StepSeconds);++K){const double T=K*StepSeconds;
  I={};C={};
  if(Case==0){I.Throttle=T<8?1:0;I.Brake=T>=8?1:0;}
  if(Case==1){I.Throttle=.25;I.Steering=.8;}
  if(Case==2){I.Throttle=.85;I.Steering=.08;}
  if(Case==3){I.Throttle=.6;I.Steering=.9;}
  if(Case==4||Case==5){
   if(T<1){I.Throttle=.8;I.Steering=Steering;}
   else if(T<1.6){I.Brake=Brake;I.Steering=Steering;}
   else {I.Throttle=std::abs(S.Beta)>Rad(2)||std::abs(S.R)>.15?.3:.8;I.Steering=Case==5?std::clamp(S.Beta*1.5-S.R*.12,-.8,.8):0;}
  }
  if(Case==6){I.Throttle=.3;I.Steering=.1;if(T>2&&T<5)C.FrontMu=C.RearMu=.42;if(std::abs(S.Beta)>Rad(3)){I.Steering=std::clamp(S.Beta*1.5-S.R*.12,-.8,.8);I.Throttle=.15;}}
  if(Case==7){I.Steering=1;}
  Step(S,P,C,I);
  M.Finite=M.Finite&&std::isfinite(S.U)&&std::isfinite(S.V)&&std::isfinite(S.R)&&S.FrontUtilization<=1.00001&&S.RearUtilization<=1.00001;
  M.MaxBeta=std::max(M.MaxBeta,std::abs(Deg(S.Beta)));M.MaxRear=std::max(M.MaxRear,std::abs(Deg(S.RearAlpha)));M.MaxFront=std::max(M.MaxFront,std::abs(Deg(S.FrontAlpha)));M.MaxYaw=std::max(M.MaxYaw,std::abs(Deg(S.R)));M.MaxSpeed=std::max(M.MaxSpeed,std::hypot(S.U,S.V));M.MinMu=std::min(M.MinMu,C.RearMu);
  if(S.Drifting)++M.DriftFrames;
  if(File&&K%4==0)std::fprintf(File,"%.4f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.3f,%.3f,%.3f,%.3f,%.5f,%.5f,%.3f,%.4f,%d\n",T,S.U,S.V,Deg(S.Beta),Deg(S.R),Deg(S.FrontAlpha),Deg(S.RearAlpha),S.FrontFx,S.RearFx,S.FrontFy,S.RearFy,S.FrontUtilization,S.RearUtilization,C.RearMu,Deg(S.Steer),S.Drifting?1:0);
 }
 if(File)std::fclose(File);
 M.EndSpeed=std::hypot(S.U,S.V);M.EndBeta=std::abs(Deg(S.Beta));M.EndYaw=std::abs(Deg(S.R));
 if(Name)std::printf("{\"case\":\"%s\",\"finite_and_grip_bounded\":%s,\"max_beta_deg\":%.3f,\"max_rear_slip_deg\":%.3f,\"max_front_slip_deg\":%.3f,\"max_yaw_deg_s\":%.3f,\"max_speed_mps\":%.3f,\"end_speed_mps\":%.3f,\"end_beta_deg\":%.3f,\"end_yaw_deg_s\":%.3f,\"drift_steps\":%d}\n",Name,M.Finite?"true":"false",M.MaxBeta,M.MaxRear,M.MaxFront,M.MaxYaw,M.MaxSpeed,M.EndSpeed,M.EndBeta,M.EndYaw,M.DriftFrames);
 return M;
}
int main(int argc,char** argv){
 const char* Names[]={"straight_brake","low_speed_tight","high_speed_grip","excessive_corner","brake_entry","countersteer_recovery","surface_transition","parked_steering"};
 for(int C=0;C<8;++C){char Path[1024];std::snprintf(Path,sizeof(Path),"%s/%s.csv",argc>1?argv[1]:".",Names[C]);Run(Names[C],C,Path);}
 if(argc>2&&std::strcmp(argv[2],"sweep")==0)for(double Speed:{9.,11.,13.})for(double Steering:{.10,.12,.15,.18,.24,.3})for(double Brake:{.20,.30,.35,.38,.40,.42,.44,.46,.48,.49,.50,.51,.52,.54,.56,.60,.8}){
  auto M=Run(nullptr,5,nullptr,Brake,Steering,Speed);
  if(M.MaxBeta>6&&M.MaxBeta<25&&M.EndBeta<2&&M.EndYaw<5&&M.DriftFrames>0)std::printf("RECOVERABLE speed=%.1f steer=%.2f brake=%.2f beta=%.2f rear=%.2f yaw=%.2f drift=%d\n",Speed,Steering,Brake,M.MaxBeta,M.MaxRear,M.MaxYaw,M.DriftFrames);
 }
}
