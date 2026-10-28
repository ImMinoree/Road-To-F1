#pragma once
#include <algorithm>
#include <cmath>

// SI units, X forward/Y right, positive yaw turns right. No Unreal/world dependency.
// The same solver is used by gameplay, the native tuning harness and automation tests.
namespace KartDynamics {
constexpr double Pi=3.14159265358979323846, StepSeconds=1.0/240.0, Gravity=9.81;
inline double Rad(double Degrees){return Degrees*Pi/180.0;}
inline double Deg(double Radians){return Radians*180.0/Pi;}
inline double Smooth(double A,double B,double X){double T=std::clamp((X-A)/(B-A),0.0,1.0);return T*T*(3-2*T);}
struct Parameters {
 double Mass=165,Inertia=65,Wheelbase=1.04,FrontDistance=.60,Track=1.06,CGHeight=.28;
 double FrontStiffness=15000,RearStiffness=21000,RearGripScale=1.10,SlidingDrop=.12;
 double EngineForce=710,BrakeForce=550,RearBrakeBias=1,LinearDrag=.32,RollingForce=15;
 double MaxSteerDegrees=24,SteerRate=2,HighSpeedSteerReduction=.75,RelaxationLength=.18,AxleScrub=8;
 double DriftEnterDegrees=6,DriftExitDegrees=3,DriftMinSpeed=3,DriftHold=.12,RecoveryHold=.18;
};
struct Contact {double FrontMu=1.05,RearMu=1.05,FrontSupport=1,RearSupport=1;};
struct Input {double Throttle=0,Steering=0,Brake=0;};
struct State {
 double X=0,Y=0,Heading=0,U=0,V=0,R=0,Steer=0,Ax=0,Ay=0;
 double FrontAlpha=0,RearAlpha=0,FrontFx=0,RearFx=0,FrontFy=0,RearFy=0;
 double FrontLoad=0,RearLoad=0,FrontCapacity=0,RearCapacity=0,FrontUtilization=0,RearUtilization=0;
 double RearLongDemand=0,Beta=0,DriftClock=0,RecoveryClock=0,RearInsideFraction=.5;
 bool Drifting=false,Oversteering=false;
 void ClearMotion(){U=V=R=Ax=Ay=FrontAlpha=RearAlpha=FrontFx=RearFx=FrontFy=RearFy=0;FrontUtilization=RearUtilization=RearLongDemand=Beta=DriftClock=RecoveryClock=0;Drifting=Oversteering=false;}
};
double MaxSteer(const Parameters& P,double Speed);
void UpdateSteering(State& S,const Parameters& P,double Steering,double Dt);
void Step(State& S,const Parameters& P,const Contact& C,const Input& I,double Dt=StepSeconds);
// SI contact impulse. Normal points from B toward A; a null B is an immovable barrier.
double ResolveContact(State& A,const Parameters& PA,State* B,const Parameters* PB,
 double AX,double AY,double BX,double BY,double PX,double PY,double NX,double NY,double Friction=.35,double Restitution=.05);
}
