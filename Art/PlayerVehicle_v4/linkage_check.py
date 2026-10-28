import math
axis=(math.cos(math.radians(55)),0,-math.sin(math.radians(55)));bottom=(23+35*axis[0],0,52+35*axis[2]);off=(8,0,8/math.tan(math.radians(55)))
def pin(a):
 a=math.radians(a);c=math.cos(a);s=math.sin(a);x,y,z=off;ax,ay,az=axis;dot=ax*x+az*z
 return (bottom[0]+x*c+ax*dot*(1-c), (az*x-ax*z)*s,bottom[2]+z*c+az*dot*(1-c))
def pickup(side,a):
 a=math.radians(a);x=-11;y=-side*4.9
 return (60+x*math.cos(a)-y*math.sin(a),side*46+x*math.sin(a)+y*math.cos(a),17.589)
def kn(side,c):
 L=math.dist(pin(0),pickup(side,0));a=c*.6
 for i in range(16):
  def e(a):return math.dist(pin(c),pickup(side,a))-L
  d=(e(a+.05)-e(a-.05))/.1
  a=max(-60,min(60,a-e(a)/d))
 return a
for c in [-45,-30,-15,0,15,30,45]:print(c,kn(-1,c),kn(1,c))
