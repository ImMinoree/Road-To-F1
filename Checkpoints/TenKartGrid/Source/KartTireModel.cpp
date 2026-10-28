#include "KartTireModel.h"

namespace KartDynamics {
double ResolveContact(State& A,const Parameters& PA,State* B,const Parameters* PB,
 double AX,double AY,double BX,double BY,double PX,double PY,double NX,double NY,double Friction,double Restitution){
 const double Length=std::hypot(NX,NY);if(Length<1e-8)return 0;
 NX/=Length;NY/=Length;
 const double InvA=1/PA.Mass,InvIA=1/PA.Inertia,InvB=B&&PB?1/PB->Mass:0,InvIB=B&&PB?1/PB->Inertia:0;
 const double RAX=PX-AX,RAY=PY-AY,RBX=PX-BX,RBY=PY-BY;
 auto Velocity=[](const State& S,double RX,double RY,double& X,double& Y){
  X=std::cos(S.Heading)*S.U-std::sin(S.Heading)*S.V-S.R*RY;
  Y=std::sin(S.Heading)*S.U+std::cos(S.Heading)*S.V+S.R*RX;
 };
 auto Apply=[](State& S,double X,double Y,double RX,double RY,double InvM,double InvI){
  S.U+=(std::cos(S.Heading)*X+std::sin(S.Heading)*Y)*InvM;
  S.V+=(-std::sin(S.Heading)*X+std::cos(S.Heading)*Y)*InvM;S.R+=(RX*Y-RY*X)*InvI;
 };
 double VAX,VAY,VBX=0,VBY=0;Velocity(A,RAX,RAY,VAX,VAY);if(B)Velocity(*B,RBX,RBY,VBX,VBY);
 const double Closing=(VAX-VBX)*NX+(VAY-VBY)*NY;if(Closing>=0)return 0;
 const double CrossA=RAX*NY-RAY*NX,CrossB=RBX*NY-RBY*NX;
 // No restitution in resting contacts: held throttle must not create repeated bounce.
 const double J=-(1+(Closing<-.5?std::clamp(Restitution,0.0,.2):0))*Closing/(InvA+InvB+CrossA*CrossA*InvIA+CrossB*CrossB*InvIB);
 Apply(A,J*NX,J*NY,RAX,RAY,InvA,InvIA);if(B)Apply(*B,-J*NX,-J*NY,RBX,RBY,InvB,InvIB);
 Velocity(A,RAX,RAY,VAX,VAY);if(B)Velocity(*B,RBX,RBY,VBX,VBY);
 const double TX=-NY,TY=NX,TA=RAX*TY-RAY*TX,TB=RBX*TY-RBY*TX;
 const double JT=std::clamp(-((VAX-VBX)*TX+(VAY-VBY)*TY)/(InvA+InvB+TA*TA*InvIA+TB*TB*InvIB),-Friction*J,Friction*J);
 Apply(A,JT*TX,JT*TY,RAX,RAY,InvA,InvIA);if(B)Apply(*B,-JT*TX,-JT*TY,RBX,RBY,InvB,InvIB);
 A.Beta=std::atan2(A.V,std::max(.1,std::abs(A.U)));if(B)B->Beta=std::atan2(B->V,std::max(.1,std::abs(B->U)));
 return J;
}
double MaxSteer(const Parameters& P,double Speed){return Rad(P.MaxSteerDegrees)/(1+P.HighSpeedSteerReduction*Speed*Speed/(18*18));}
void UpdateSteering(State& S,const Parameters& P,double Steering,double Dt){
 const double Desired=std::clamp(Steering,-1.0,1.0)*MaxSteer(P,std::abs(S.U));
 S.Steer+=std::clamp(Desired-S.Steer,-P.SteerRate*Dt,P.SteerRate*Dt);
}
void Step(State& S,const Parameters& P,const Contact& C,const Input& I,double Dt){
 UpdateSteering(S,P,I.Steering,Dt);
 const double M=P.Mass,A=P.FrontDistance,B=P.Wheelbase-A;
 const double Co=std::cos(S.Steer),Si=std::sin(S.Steer),Speed=std::hypot(S.U,S.V);
 // Quasi-static load transfer, bounded before using the previous physical acceleration.
 const double Transfer=std::clamp(M*S.Ax*P.CGHeight/P.Wheelbase,-M*Gravity*.3,M*Gravity*.3);
 S.FrontLoad=std::clamp(M*Gravity*B/P.Wheelbase-Transfer,M*Gravity*.12,M*Gravity*.88);
 S.RearLoad=M*Gravity-S.FrontLoad;
 const double LateralTransfer=std::min(M*std::abs(S.Ay)*P.CGHeight/P.Track,M*Gravity*.49);
 auto LoadFactor=[&](double Load,double TransferShare){
  const double Inside=std::max(0.0,Load*.5-LateralTransfer*TransferShare),Outside=Load-Inside;
  return .5*(std::pow(2*Inside/Load,.90)+std::pow(2*Outside/Load,.90));
 };
 S.RearInsideFraction=std::max(0.0,.5-LateralTransfer*(A/P.Wheelbase)/S.RearLoad);
 S.FrontAlpha=std::atan2(-Si*S.U+Co*(S.V+A*S.R),std::max(2.0,std::abs(Co*S.U+Si*(S.V+A*S.R))));
 S.RearAlpha=std::atan2(S.V-B*S.R,std::max(2.0,std::abs(S.U)));
 // Smooth peak-to-sliding transition, with sensitivity to unequal left/right wheel loads.
 S.FrontCapacity=std::max(0.0,C.FrontMu*S.FrontLoad*LoadFactor(S.FrontLoad,B/P.Wheelbase)*C.FrontSupport*(1-P.SlidingDrop*Smooth(.10,.40,std::abs(S.FrontAlpha))));
 S.RearCapacity=std::max(0.0,C.RearMu*P.RearGripScale*S.RearLoad*LoadFactor(S.RearLoad,A/P.Wheelbase)*C.RearSupport*(1-P.SlidingDrop*Smooth(.10,.40,std::abs(S.RearAlpha))));
 double Brake=std::clamp(I.Brake,0.0,1.0),Drive=std::clamp(I.Throttle,-1.0,1.0);
 if(Drive*S.U<0&&std::abs(S.U)>.35){Brake=std::max(Brake,std::abs(Drive));Drive=0;}
 if(Brake>0)Drive=0;
 double DriveForce=Drive*P.EngineForce;
 if(Drive<0)DriveForce*=.65*(1-Smooth(2.5,3.5,-S.U));
 const double Direction=S.U>.02?1:(S.U<-.02?-1:0);
 const double BrakeRequest=Brake*P.BrakeForce*Direction;
 const double FrontRequest=-BrakeRequest*(1-P.RearBrakeBias),RearRequest=DriveForce-BrakeRequest*P.RearBrakeBias;
 S.FrontFx=std::clamp(FrontRequest,-S.FrontCapacity*.985,S.FrontCapacity*.985);
 S.RearFx=std::clamp(RearRequest,-S.RearCapacity*.985,S.RearCapacity*.985);
 S.RearLongDemand=std::abs(RearRequest)/std::max(1.0,S.RearCapacity);
 const double FrontLateral=std::sqrt(std::max(0.0,S.FrontCapacity*S.FrontCapacity-S.FrontFx*S.FrontFx));
 const double RearLateral=std::sqrt(std::max(0.0,S.RearCapacity*S.RearCapacity-S.RearFx*S.RearFx));
 auto Tire=[&](double Alpha,double Stiffness,double Load,double StaticLoad,double Available,double Previous){
  if(Available<.01)return 0.0;
  const double Target=-Available*std::tanh(Stiffness*std::pow(Load/StaticLoad,.85)*Alpha/Available);
  const double Tau=std::clamp(P.RelaxationLength/std::max(1.0,Speed),.012,.08);
  return std::clamp(Previous+(Target-Previous)*(1-std::exp(-Dt/Tau)),-Available,Available);
 };
 S.FrontFy=Tire(S.FrontAlpha,P.FrontStiffness,S.FrontLoad,M*Gravity*B/P.Wheelbase,FrontLateral,S.FrontFy);
 S.RearFy=Tire(S.RearAlpha,P.RearStiffness,S.RearLoad,M*Gravity*A/P.Wheelbase,RearLateral,S.RearFy);
 S.FrontUtilization=std::hypot(S.FrontFx,S.FrontFy)/std::max(1.0,S.FrontCapacity);
 S.RearUtilization=std::hypot(S.RearFx,S.RearFy)/std::max(1.0,S.RearCapacity);
 const double Fx=S.FrontFx*Co-S.FrontFy*Si+S.RearFx-M*P.LinearDrag*S.U-P.RollingForce*std::tanh(S.U*3);
 const double Fy=S.FrontFy*Co+S.FrontFx*Si+S.RearFy;
 // Locked rear axle resists differential wheel travel. Inside unloading relieves scrub.
 const double ScrubTorque=-P.AxleScrub*S.R*(S.RearInsideFraction*2)*std::min(1.0,Speed);
 const double Torque=A*(S.FrontFy*Co+S.FrontFx*Si)-B*S.RearFy+ScrubTorque;
 S.Ax=Fx/M;S.Ay=Fy/M;
 const double OldU=S.U;
 S.U+=(S.Ax+S.R*S.V)*Dt;S.V+=(S.Ay-S.R*OldU)*Dt;S.R+=Torque/P.Inertia*Dt;
 if(Brake>0&&OldU*S.U<0)S.U=0; // A brake cannot propel the kart backwards.
 if(std::abs(Drive)<.001&&std::abs(S.U)<.025&&std::abs(S.V)<.025&&std::abs(S.R)<.03)S.ClearMotion();
 S.Heading=std::remainder(S.Heading+S.R*Dt,2*Pi);
 const double Cos=std::cos(S.Heading),Sin=std::sin(S.Heading);
 S.X+=(Cos*S.U-Sin*S.V)*Dt;S.Y+=(Sin*S.U+Cos*S.V)*Dt;
 S.Beta=std::atan2(S.V,std::max(.1,std::abs(S.U)));
 const bool Enter=Speed>P.DriftMinSpeed&&std::abs(S.V)>.35&&std::abs(S.Beta)>Rad(P.DriftEnterDegrees)&&std::abs(S.RearAlpha)>Rad(4)&&S.RearUtilization>.6;
 const bool Exit=Speed<P.DriftMinSpeed*.8||std::abs(S.Beta)<Rad(P.DriftExitDegrees)||std::abs(S.RearAlpha)<Rad(2);
 if(!S.Drifting){S.DriftClock=Enter?S.DriftClock+Dt:0;if(S.DriftClock>=P.DriftHold){S.Drifting=true;S.RecoveryClock=0;}}
 else {S.RecoveryClock=Exit?S.RecoveryClock+Dt:0;if(S.RecoveryClock>=P.RecoveryHold){S.Drifting=false;S.DriftClock=0;}}
 S.Oversteering=S.Drifting&&std::abs(S.RearAlpha)>std::abs(S.FrontAlpha)+Rad(1);
}
}
