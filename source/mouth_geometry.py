"""Organic mouth and 16:64 external involute gears, all geometry in mm."""
import math,json
import numpy as np
import base_geometry as b
from base_geometry import box,cyl,cx,tube,sphere,beamx
U=np.array([0.,-50.,8.]);L=np.array([0.,-50.,-32.])
LEFT_ARM=-51.4; GEAR_X=-45.; FRAME_LEFT=-38.; SERVO_SHIFT=19.
TEETH=[]
SOCKETS=[]
ROOT_RADIUS=2.8
ROOT_FLAT=1.9
ROOT_LENGTH=6.5
SOCKET_CLEARANCE=.25
SOCKET_DEPTH=7.2


def d_profile(radius,flat,z,height):
    return cyl(0,0,z,radius,height)^box(-radius-1,-radius-1,z-.1,radius+1+flat,2*radius+2,height+.2)


def digit_bars(number):
    """Seven-segment number in a 1.8 x 3.4 mm rectangle."""
    bars={'a':(-.9,3.05,1.8,.35),'g':(-.9,1.525,1.8,.35),'d':(-.9,0,1.8,.35),
          'f':(-.9,1.7,.35,1.5),'b':(.55,1.7,.35,1.5),'e':(-.9,.2,.35,1.5),'c':(.55,.2,.35,1.5)}
    chars={1:'bc',2:'abged',3:'abgcd',4:'fgbc',5:'afgcd',6:'afgecd',7:'abc',8:'abcdefg'}
    return [bars[k] for k in chars[number]]


def tooth_root(number=0):
    pin=d_profile(ROOT_RADIUS,ROOT_FLAT,-.3,ROOT_LENGTH-.6+.3)
    tip=b.M.cylinder(.6,ROOT_RADIUS,ROOT_RADIUS-.4,circular_segments=64).translate((0,0,ROOT_LENGTH-.6))
    tip=tip^box(-4,-4,ROOT_LENGTH-.7,ROOT_FLAT+4,8,.8)
    pin=pin+tip
    if number:
        for u,v,w,h in digit_bars(number):pin-=box(ROOT_FLAT-.18,u,1.2+v,.4,w,h)
    return pin


def socket_cut(clearance=SOCKET_CLEARANCE):
    hole=d_profile(ROOT_RADIUS+clearance,ROOT_FLAT+clearance,-.2,SOCKET_DEPTH+.2)
    lead=b.M.cylinder(.55,ROOT_RADIUS+clearance+.4,ROOT_RADIUS+clearance,circular_segments=64)
    lead=lead^box(-4,-4,-.1,ROOT_FLAT+clearance+.4+4,8,.8)
    return hole+lead


def install(s,a,upper,origin):
    return s.rotate((0 if upper else 180,0,math.degrees(a))).translate(origin)


def dentition(upper):
    bosses=[];cuts=[]
    angles=[5,25,45,65,115,135,155,175] if upper else [15,35,55,125,145,165]
    for i,a in enumerate(np.radians(angles)):
        raw=fang(a,upper,i);t=TEETH[-1]
        origin=np.array(t['points'][0]);z=origin[2]
        # A true planar root shoulder, keeping the exposed fang silhouette.
        clip=box(-130,-130,z-100 if upper else z,260,260,100)
        crown=raw^clip
        collar=install(cyl(0,0,-.6,5.25,.6),a,upper,origin)
        root=install(tooth_root(i+1),a,upper,origin)
        tooth=crown+collar+root
        id=('U' if upper else 'L')+str(i+1).zfill(2)
        # Tooth long axis lies along bed X; exposed crown remains uncut.
        b.add(id,('Upper' if upper else 'Lower')+' removable tooth '+str(i+1),tooth,'bone','upper' if upper else 'lower',orientation=(0,90,0))
        boss=install(b.M.cylinder(9.4,7.8,6.5,circular_segments=64),a,upper,origin)
        # Existing lip material partly surrounds each crown. Clearance relief
        # removes only that contact so the tooth can slide fully into its seat.
        relief=tube(np.array(t['points']),np.array(t['radii'])+.18,32)
        # Conservatively sweep the curved crown out of the mouth. A final-pose
        # relief alone would trap the wider crown while inserting it axially.
        outward=np.array([0.,0.,-18. if upper else 18.])
        relief=b.union([relief,relief.translate(outward)]).hull()
        relief=relief^clip
        # The swept tube starts with a slightly tilted cap. A planar counterseat
        # clears that cap and gives the crown's flat shoulder a true depth stop.
        shoulder=install(cyl(0,0,-.8,6.05,.8),a,upper,origin)
        cavity=install(socket_cut(),a,upper,origin)
        bosses.append(boss);cuts.extend([cavity,relief,shoulder])
        SOCKETS.append(dict(id=id,jaw='C01' if upper else 'C02',upper=upper,angle_deg=float(math.degrees(a)),origin=origin.tolist(),axis_into_jaw=[0,0,1 if upper else -1],pin_radius_mm=ROOT_RADIUS,flat_offset_mm=ROOT_FLAT,pin_length_mm=ROOT_LENGTH,clearance_per_side_mm=SOCKET_CLEARANCE,socket_depth_mm=SOCKET_DEPTH,boss_depth_mm=9.4,crown_relief_mm=.18,insertion_sweep_mm=18))
    return b.union(bosses),b.union(cuts)


def fit_coupon():
    block=box(0,0,0,66,20,11)
    for i,clearance in enumerate([.20,.25,.30]):
        x=11+22*i
        block-=socket_cut(clearance).rotate((180,0,0)).translate((x,10,11))
        for j in range(i+1):block-=cyl(x-1.3*i+2.6*j,3,10.5,.65,1)
    b.add('T02','D-root socket coupon - one two three dots = 0.20 0.25 0.30 mm clearance',block,'mech','test')
    test=box(-4,-6,-3,8,12,3)+tooth_root(1)
    b.add('T03','D-root fit key - same root as teeth',test,'bone','test',orientation=(0,90,0))

def lip(upper):
    rx,ry,zc=(84,78,25) if upper else (73,73,-.5)
    verts=[];faces=[];na,nb=384,40
    for i in range(na):
        a=2*np.pi*i/na;front=max(0,np.sin(a))
        w=(6.+4.8*front**.7 if upper else 7.+3.3*front**.6)+.45*np.sin(3*a+.4)
        h=(4.1+3.8*front**.7 if upper else 5.3+2.1*front**.6)+.25*np.sin(4*a)
        z=zc+.45*np.sin(2*a)+.32*np.sin(5*a+.3)
        for j in range(nb):
            t=2*np.pi*j/nb
            # Fine shallow vertical folds on a broad irregular flesh volume.
            fold=.13*np.sin(a*67+1.8*np.sin(7*a))*.6+.1*np.sin(a*113+t*.9)
            rad=w+fold*(.5+.5*np.cos(t))
            verts.append([(rx+rad*np.cos(t))*np.cos(a),(ry+rad*np.cos(t))*np.sin(a),z+(h+.45*fold)*np.sin(t)])
    for i in range(na):
        for j in range(nb):
            a=i*nb+j;c=i*nb+(j+1)%nb;d=((i+1)%na)*nb+(j+1)%nb;e=((i+1)%na)*nb+j
            faces.extend([[a,e,c],[e,d,c]])
    return b.from_mesh(verts,faces)

def fang(a,upper,index):
    rad=np.array([np.cos(a),np.sin(a),0.])
    x,y=(72*np.cos(a),68*np.sin(a)) if upper else (68*np.cos(a),68*np.sin(a))
    z=28 if upper else -1
    length=(27+2*np.sin(index*1.9)) if upper else (18+2*np.cos(index*1.7))
    bend=(14 if abs(np.cos(a))>.8 and np.sin(a)>.2 else 10) if upper else 2.5
    pts=[];rs=[]
    for t in np.linspace(0,1,25):
        pts.append(np.array([x,y,z])-rad*bend*t*t+np.array([.6*np.sin(index)*t*t,0,(-1 if upper else 1)*length*t]))
        rs.append(.85+(4.9 if upper else 4.6)*(1-t)**1.35)
    TEETH.append(dict(upper=upper,points=np.array(pts).tolist(),radii=rs))
    return tube(pts,rs,32)

def organic():
    shell=b.organic_hemisphere(84,78,68,10).translate((0,0,13))
    # Reconstruct the same seeded plaques used by the earlier skull.
    rng=np.random.default_rng(482)
    spots=json.loads((b.ROOT/'validation'/'spot_centers.json').read_text())
    for c,n in spots:
        c=np.array(c);n=np.array(n)
        p=b.M.sphere(1,48).scale((rng.uniform(6,10),rng.uniform(5,8),2.4))
        axis=np.cross([0,0,1],n);angle=math.acos(n[2])
        mat=b.trimesh.transformations.rotation_matrix(angle,axis) if np.linalg.norm(axis)>1e-8 else np.eye(4)
        shell+=p.transform(mat[:3,:4]).translate(c-n*.65+[0,0,13])
    shell+=lip(True)
    bosses,cuts=dentition(True);shell+=bosses
    for x,y in [(-48,20),(48,20),(0,-64)]:
        if x:pad=box(min(x,math.copysign(73,x))-5,y-5,20,abs(x-math.copysign(73,x))+10,10,5)
        else:pad=box(-6,-79,20,12,21,5)
        pad-=cyl(x,y,18,1.7,12);pad-=cyl(x,y,22.5,3.25,4,6);shell+=pad
    shell-=cuts
    b.add('C01','Upper skull and plump lip with eight keyed tooth sockets',shell,'red','upper')
    lower=(b.organic_hemisphere(74,74,48,0,-1)+lip(False))^box(-100,-8,-80,200,120,100)
    bosses,cuts=dentition(False);lower+=bosses
    # Two jaw hinge arms and a central tongue/electronics deck fused to the bowl.
    for x in [LEFT_ARM,54]:
        lower+=beamx((-50,-32),(8,-30),5,x,6)+cx(x,-50,-32,9 if x>0 else 14,6)
        lower-=cx(x-1,-50,-32,2.2,8)
    for a in np.radians([0,120,240]):
        y=-50+10*np.cos(a);z=-32+10*np.sin(a);lower-=cx(LEFT_ARM-1,y,z,1.7,8)
        lower-=cx(LEFT_ARM-1,y,z,3.2,1.8)
    # Flat deck rides with the lower jaw; mounting holes accept removable root.
    lower+=box(-39,-7,-13,78,54,4)
    for sg in [-1,1]:lower+=box(33 if sg>0 else -53,8,-31,20,10,22)
    lower+=box(-26,-28,-13,52,25,4)
    # Tie-mounted MG90S compartment below the deck; shaft points right.
    lower+=box(0,-22,-29,32,31,3)
    lower+=box(0,-22,-29,32,2.4,18)+box(0,5.3,-29,32,3.7,18)
    for yy in [-18,-2]:lower-=box(4,yy,-30,23,3.2,5)
    for xx in [-19,39]:lower-=cyl(xx,18,-15,1.7,12)
    # Rear stem clearance remains open, with 12.5-degree jaw travel only.
    lower-=box(-28,-80,-70,56,48,45)
    lower-=cuts
    b.add('C02','Lower jaw and tongue tray with six keyed tooth sockets',lower,'jaw','lower')
    fit_coupon()
    (b.ROOT/'validation'/'teeth.json').write_text(json.dumps(TEETH))
    (b.ROOT/'validation'/'tooth_sockets.json').write_text(json.dumps(SOCKETS,indent=2))

def gear(n,phase):
    # 25-degree pressure angle avoids undercut on the small 16-tooth pinion.
    rp=n/2;rb=rp*np.cos(np.radians(25));ra=rp+1;rf=rp-1.25
    inv=lambda r: math.sqrt(max(0,(r/rb)**2-1))-math.acos(min(1,rb/r))
    half=np.pi/(2*n)-.10/(2*rp) # 0.20 mm pair backlash at the pitch circles
    pts=[]
    for i in range(n):
        a=phase+i*2*np.pi/n
        rs=np.r_[rf,np.linspace(max(rb,rf),ra,12)]
        for rr in rs:
            ang=a-half-inv(rp)+inv(max(rb,rr));pts.append([rr*np.cos(ang),rr*np.sin(ang)])
        tip=half+inv(rp)-inv(ra)
        for ang in np.linspace(a-tip,a+tip,5)[1:]:pts.append([ra*np.cos(ang),ra*np.sin(ang)])
        for rr in rs[-2::-1]:
            ang=a+half+inv(rp)-inv(max(rb,rr));pts.append([rr*np.cos(ang),rr*np.sin(ang)])
    return b.m.CrossSection([np.array(pts)]).extrude(6).rotate((90,0,90))

def mechanism():
    frame=box(-26,-74,-23.6,52,37,5.6)-cyl(0,-59,-25,9,10)
    for x,y in [(-17,-59),(17,-59),(0,-42)]:frame-=cyl(x,y,-25,2.25,12)
    frame+=box(FRAME_LEFT,-65,-17,53-FRAME_LEFT,8,7)
    frame+=box(-26,-65,-20,52,8,7)
    for x in [FRAME_LEFT,45]:
        frame+=beamx((-61,-13),(-50,-32),5,x,8)+cx(x,-50,-32,8,8)
        frame-=cx(x-1,-50,-32,2.2,10)
    frame+=beamx((-61,-13),(-50,8),5,45,8)+cx(45,-50,8,8,8)
    frame-=cx(44,-50,8,2.2,10)
    cradle=box(-51,-66,-5.5,47,54,3)
    cradle+=box(-51,-66,-4,4,54,24)+box(-51,-66,-4,47,4,24)+box(-51,-16,-4,47,4,24)
    cradle-=box(-49,-61,-2.5,46,42,29);cradle-=cx(-54,-50,8,7.2,8)
    for yy in [-56,-26]:cradle-=box(-54,yy,-4,9,4,24)
    cradle+=box(-49,-63,-13,8,22,10)
    cradle-=box(-54,-68,0,54,8,30)
    frame+=cradle.translate((SERVO_SHIFT,0,0))
    for y,z,anchor in [(-71,-20,(-61,-13)),(-68,-40,(-50,-32))]:
        frame+=beamx(anchor,(y,z),4,FRAME_LEFT,8)+cx(FRAME_LEFT,y,z,4.5,8)
        frame-=cx(FRAME_LEFT-1,y,z,1.7,10)
    b.add('C04','Stationary twin hinge frame and MG995 cradle',frame,'gums','head')
    carrier=b.M()
    for x in [LEFT_ARM,54]:
        carrier+=beamx((-50,8),(20,14),5,x,6)+beamx((-50,8),(-64,15),4.5,x,6)
        carrier+=cx(x,-50,8,10,6)
        carrier-=cx(x-1,-50,8,2.8 if x<0 else 2.2,8)
        carrier+=box(-54 if x<0 else 42,14,16,12 if x<0 else 18,12,3.6)
    carrier+=box(LEFT_ARM,-67,15.6,60-LEFT_ARM,6,4)
    for x,y in [(-48,20),(48,20),(0,-64)]:carrier-=cyl(x,y,13,1.7,12)
    for zz in [-4.8,4.8]:carrier-=cx(LEFT_ARM-1,-50,8+zz,1.1,9)
    b.add('G00','Upper carrier for internal gear stack',carrier,'gums','upper')
    g=gear(16,-np.pi/2).translate((GEAR_X,-50,8))-cx(GEAR_X-1,-50,8,2.8,8)
    for zz in [-4.8,4.8]:g-=cx(GEAR_X-1,-50,8+zz,1.1,8)
    b.add('G01','16 tooth upper drive pinion module 1',g,'gold','upper',orientation=(0,90,0))
    g=gear(64,np.pi/2+np.pi/64).translate((GEAR_X,-50,-32))
    angles=np.radians(np.linspace(45,135,31))
    pts=np.array([[0,0]]+[[40*np.cos(a),40*np.sin(a)] for a in angles])
    wedge=b.m.CrossSection([pts]).extrude(8).rotate((90,0,90)).translate((GEAR_X-1,-50,-32))
    g=g^(wedge+cx(GEAR_X-1,-50,-32,14,8))
    g-=cx(GEAR_X-1,-50,-32,2.2,8)
    for a in np.radians([0,120,240]):
        y=-50+10*np.cos(a);z=-32+10*np.sin(a)
        g-=cx(GEAR_X-1,y,z,1.7,8)
        g-=cx(GEAR_X+3.2,y,z,3.25,3.8,6)
    b.add('G02','Quarter sector of 64 tooth gear - 16 retained teeth',g,'gold','lower',orientation=(0,90,0))
    spacer=cx(-39,-50,8,7,2)-cx(-40,-50,8,2.8,4)
    for zz in [-4.8,4.8]:spacer-=cx(-40,-50,8+zz,1.1,4)
    b.add('G03','Two millimetre horn spacer',spacer,'gums','upper',orientation=(0,90,0))
    cheek()


def cheek():
    center=np.array([-48.,-53.,-11.]);radii=np.array([12.,29.,39.])
    vv,ff=b.meshdata(sphere(center,1,radii,128))
    normals=(vv-center)/(radii*radii);normals/=np.linalg.norm(normals,axis=1)[:,None]
    relief=.16*np.sin(vv[:,1]*1.5+np.sin(vv[:,2]*.8))+.1*np.sin(vv[:,2]*2.4+vv[:,1]*.7)
    skin=b.from_mesh(vv+normals*relief[:,None],ff)-sphere(center,1,radii-2.8,128)
    skin=skin^box(-70,-90,-60,17,80,100)
    skin=skin^box(-75,-95,-65,50,95,84.5)
    # Rounded rear notch follows the rising skull's back edge.
    skin-=cx(-71,-83,29,28,22)
    for y,z in [(-71,-20),(-68,-40)]:
        skin+=cx(-57,y,z,3.8,18)
        skin-=cx(-62,y,z,1.7,24)
        skin-=cx(-62,y,z,3.2,5)
    b.add('C18','Removable textured left cheek gear cover',skin,'jaw','head',orientation=(0,90,0))

def colors(v,p):
    col=ORIGINAL_COLORS(v,p)
    if p['id'] not in ['C01','C02']:return col
    if p['id']=='C02':col[(col[:,0]>190)&(col[:,1]>160)]=[110,46,53]
    upper=p['id']=='C01';rx,ry,zc=(84,78,25) if upper else (73,73,-.5)
    radial=np.sqrt((v[:,0]/rx)**2+(v[:,1]/ry)**2)
    # Broad flesh hue with a warm central highlight and a burgundy attachment edge.
    mask=(abs(radial-1)<.15)&(abs(v[:,2]-zc)<9.5)
    flesh=np.array([171,98,94.]);noise=(.92+.08*np.sin(v[:,0]*.11+v[:,1]*.15))[:,None]
    col[mask]=np.clip(flesh*noise[mask],0,255)
    # The crown solids now have their own ivory material; gums stay organic.
    return col

ORIGINAL_COLORS=b.color_vertices
