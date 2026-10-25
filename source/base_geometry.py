"""Piranha cuckoo clock, millimetres. Deterministic printable geometry.

Run from any directory with requirements.txt installed. Outputs are overwritten
only within this project's generated cad/, stl/, and validation/ directories.
Organic parts are closed meshes, deliberately retained as meshes in Rhino.
"""
from pathlib import Path
import math, json, csv, os
import numpy as np
import manifold3d as m
try:
    import rhino3dm as r
    if not hasattr(r, 'File3dm'): from rhino3dm import _rhino3dm as r
except ImportError:
    from rhino3dm import _rhino3dm as r
import trimesh

ROOT=Path(__file__).resolve().parents[1]
M=m.Manifold
Z=265.0
PIV=np.array([0.,-40.,0.])
PARTS={}
COLORS={'red':(124,25,29),'jaw':(113,22,29),'gums':(77,29,37),'green':(56,82,34),'leaf':(68,91,37),'pipe':(24,74,48),'soil':(39,34,25),'tongue':(144,48,64),'mech':(75,83,78),'gold':(167,124,56),'bone':(213,193,145),'black':(22,25,24),'board':(24,110,119)}

def box(x,y,z,a,b,c): return M.cube((a,b,c)).translate((x,y,z))
def cyl(x,y,z,rad,h,n=64): return M.cylinder(h,rad,circular_segments=n).translate((x,y,z))
def cx(x,y,z,rad,h,n=48): return M.cylinder(h,rad,circular_segments=n).rotate((0,90,0)).translate((x,y,z))
def cy(x,y,z,rad,h,n=64): return M.cylinder(h,rad,circular_segments=n).rotate((-90,0,0)).translate((x,y,z))
def union(xs):
    xs=list(xs)
    return M.batch_boolean(xs,m.OpType.Add) if xs else M()
def sphere(c,rad,sc=(1,1,1),n=48):return M.sphere(rad,n).scale(sc).translate(c)
def beamx(a,b,rad,x,thick):return (cx(x,*a,rad,thick)+cx(x,*b,rad,thick)).hull()
def tube(points,radii,n=16):
    p=np.asarray(points,float); radii=np.broadcast_to(np.asarray(radii,float),(len(p),))
    ts=np.gradient(p,axis=0);ts/=np.linalg.norm(ts,axis=1)[:,None]
    ref=np.tile([1.,0,0],(len(p),1));mask=np.abs(ts[:,0])>.85;ref[mask]=[0,1.,0]
    u=np.cross(ts,ref);u/=np.linalg.norm(u,axis=1)[:,None];v=np.cross(ts,u)
    ang=np.arange(n)*2*np.pi/n
    verts=(p[:,None,:]+radii[:,None,None]*(np.cos(ang)[None,:,None]*u[:,None,:]+np.sin(ang)[None,:,None]*v[:,None,:])).reshape(-1,3)
    verts=np.vstack([verts,p[0],p[-1]])
    fs=[]
    for j in range(len(p)-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n;c=(j+1)*n+i;d=(j+1)*n+(i+1)%n
            fs.extend([[a,b,c],[b,d,c]])
    for i in range(n):fs.extend([[len(verts)-2,(i+1)%n,i],[len(verts)-1,(len(p)-1)*n+i,(len(p)-1)*n+(i+1)%n]])
    return from_mesh(verts,fs)
def from_mesh(v,f):
    tm=trimesh.Trimesh(vertices=np.array(v),faces=np.array(f),process=True)
    trimesh.repair.fix_normals(tm,multibody=True)
    if tm.volume<0:tm.invert()
    s=M(m.Mesh64(np.asarray(tm.vertices,np.float64),np.asarray(tm.faces,np.uint64)))
    assert s.status()==m.Error.NoError, str(s.status())
    return s
def meshdata(s):
    q=s.to_mesh64();return np.asarray(q.vert_properties[:,:3]),np.asarray(q.tri_verts)
def rotate_jaw(s,q):return s.translate(-PIV).rotate((-q,0,0)).translate(PIV)
def slider_position(q,version):
    ang=math.radians(q)
    radius,zc=(42.,0.) if version==1 else (25.,17.)
    y=-40+radius*math.sin(ang);z=zc+radius*math.cos(ang)
    sy=y+math.sqrt(75**2-(z+11)**2)
    return sy, (y,z)
Y0=slider_position(0,1)[0]
def add(id,name,s,color,group='fixed',variant='common',orientation=(0,0,0)):
    assert s.status()==m.Error.NoError,(id,s.status())
    # A printable file is exactly one connected watertight solid.
    ds=s.decompose()
    assert len([d for d in ds if d.volume()>1e-7])==1,(id,name,'components',len(ds),[d.volume() for d in ds])
    PARTS[id]=dict(id=id,name=name,s=s,color=color,group=group,variant=variant,orientation=orientation)
    print(id,name,'triangles',s.num_tri(),flush=True)
    return s

def organic_hemisphere(rx,ry,rz,zc,sign=1,wall=3.2):
    # Near-uniform grid, multi-scale relief blended to smooth attachment rim.
    nu,nv=256,88
    verts=[]
    for inner in [False,True]:
        for j in range(nv+1):
            t=.0008+(math.pi/2-.0008)*j/nv
            for i in range(nu):
                a=i*2*math.pi/nu
                xyz=np.array([rx*math.sin(t)*math.cos(a),ry*math.sin(t)*math.sin(a),sign*rz*math.cos(t)])
                fade=min(1.,max(0.,(math.pi/2-t)*9))*min(1.,math.sin(t)*4)
                x,y,z=xyz
                relief=fade*(.34*math.sin(x*.68+math.sin(z*.33))*math.sin(y*.71)+.23*math.sin(z*1.23+y*.4)+.36*math.sin(a*23+4*math.sin(t*6))**6)
                if inner:
                    xyz*=np.array([(rx-wall)/rx,(ry-wall)/ry,(rz-wall)/rz]);relief=.13*math.sin(a*28+t*6)*fade
                norm=xyz/np.array([rx*rx,ry*ry,rz*rz]);norm/=np.linalg.norm(norm)
                xyz+=norm*relief;xyz[2]+=zc;verts.append(xyz)
    faces=[];N=(nv+1)*nu
    for side in [0,1]:
        offset=side*N
        for j in range(nv):
            for i in range(nu):
                a=offset+j*nu+i;b=offset+j*nu+(i+1)%nu;c=a+nu;d=b+nu
                faces.extend([[a,b,c],[b,d,c]] if side==0 else [[a,c,b],[b,c,d]])
    for i in range(nu):
        k=(i+1)%nu
        for j,rev in [(0,False),(nv,True)]:
            a=j*nu+i;b=j*nu+k;c=N+a;d=N+b
            faces.extend([[a,c,b],[b,c,d]] if rev else [[a,b,c],[b,d,c]])
    return from_mesh(verts,faces)

def lip(rx,ry,z,rad,lower=False):
    nu,nv=320,24;v=[];f=[]
    for i in range(nu):
        a=2*np.pi*i/nu
        for j in range(nv):
            b=2*np.pi*j/nv
            rr=rad+.28*math.sin(a*88+.6*math.sin(b*3))+.17*math.cos(a*47)
            v.append([(rx+rr*np.cos(b))*np.cos(a),(ry+rr*np.cos(b))*np.sin(a),z+rr*.83*np.sin(b)])
    for i in range(nu):
        for j in range(nv):
            a=i*nv+j;b=((i+1)%nu)*nv+j;c=i*nv+(j+1)%nv;d=((i+1)%nu)*nv+(j+1)%nv
            f.extend([[a,b,c],[b,d,c]])
    return from_mesh(v,f)

def tooth(x,y,z,length,sign,i):
    radial=np.array([x,y,0.]);radial/=np.linalg.norm(radial)
    ps=[];rs=[]
    for t in np.linspace(0,1,13):
        p=np.array([x,y,z])-radial*(3.5*t*t)+np.array([.8*math.sin(i)*t,0,sign*length*t])
        ps.append(p);rs.append(.7+(3.1+.35*math.sin(i))*(1-t)**1.2)
    return tube(ps,rs,18)

def build_organic():
    shell=organic_hemisphere(84,78,68,10)
    # irregular flattened fungal plaques physically fused into the skin
    rng=np.random.default_rng(482)
    spots=[]
    for t,a in [(0.27,0.2),(.49,2.0),(.67,4.2),(.83,.6),(.88,2.85),(1.05,5.0),(1.25,1.5),(1.29,3.75),(1.22,5.9),(.62,5.65),(1.39,.22),(1.42,2.35),(.39,3.6),(1.1,3.05),(1.39,4.7),(1.0,1.97)]:
        c=np.array([84*np.sin(t)*np.cos(a),78*np.sin(t)*np.sin(a),68*np.cos(t)+10])
        n=(c-[0,0,10])/np.array([84**2,78**2,68**2]);n/=np.linalg.norm(n)
        patch=M.sphere(1,48).scale((rng.uniform(6,10),rng.uniform(5,8),2.4))
        axis=np.cross([0,0,1],n);angle=math.degrees(math.acos(n[2]))
        # trimesh supplies a stable general-axis transform
        mat=trimesh.transformations.rotation_matrix(math.radians(angle),axis) if np.linalg.norm(axis)>1e-8 else np.eye(4)
        patch=patch.transform(mat[:3,:4]).translate(c-n*.65)
        spots.append((c.tolist(),n.tolist()))
        shell+=patch
    (ROOT/'validation'/'spot_centers.json').write_text(json.dumps(spots))
    shell+=lip(82,76,10,5.6)
    for i,a in enumerate(np.linspace(-.15,math.pi+.15,19)):
        x,y=78*np.cos(a),72*np.sin(a)
        shell+=tooth(x,y,9,13+4*(.5+.5*math.sin(i*2.3)), -1,i)
    # Nut-bearing pads: screws enter from the open mouth, accessible after jaw opens.
    for x,y in [(-48,20),(48,20),(0,-64)]:
        if x: pad=box(min(x,math.copysign(73,x))-5,y-5,7,abs(x-math.copysign(73,x))+10,10,5)
        else:pad=box(-6,-79,7,12,21,5)
        pad-=cyl(x,y,5,1.7,12)
        pad-=cyl(x,y,9.5,3.25,4,n=6)
        shell+=pad
    add('C01','Textured upper skull, lips and 19 fangs',shell.translate((0,0,13)),'red','head',orientation=(0,0,0))
    lower=organic_hemisphere(74,74,48,0,sign=-1)+lip(72,72,0,5.2)
    lower=lower^box(-100,-8,-80,200,120,90)
    for i,a in enumerate(np.linspace(.08,math.pi-.08,17)):
        if i in [7,8,9]:continue # central tongue escape gap
        # Different dental radius and stagger eliminate closed-pose interpenetration.
        x,y=65*np.cos(a),65*np.sin(a)
        lower+=tooth(x,y,-1,9+3*(.5+.5*math.cos(i*2.1)),1,i+3)
    for x in [-56.5,56.5]:
        lower+=beamx((-40,0),(3,-31),4.5,x-3,6)
        lower+=cx(x-3,-40,0,8,6)
        lower-=cx(x-4,-40,0,2.2,8)
    # left driven crank: exactly 18 mm, parallelogram matched to servo crank
    lower+=beamx((-40,0),(-22,0),5,-64,7)
    lower+=box(-64,-44,-3,10,8,6)
    lower-=cx(-66,-40,0,2.2,16);lower-=cx(-65,-22,0,1.65,10)
    # right removable 42-mm rocker mounts to this jaw lug at 2 separated points
    lower+=beamx((-40,0),(-1,-35),4.5,28,4)
    lower+=box(28,-5,-38,15,9,7)
    lower-=cx(27,-40,0,2.2,8);lower-=cx(27,-24,-16,1.65,9)
    lower-=M.cylinder(68,1,circular_segments=96).scale((26,46,1)).translate((0,-10,-65))
    add('C02','Textured lower jaw, 14 fangs and hinge arms',lower,'jaw','jaw',orientation=(0,0,0))
    # Molded tongue: broad rippled top, curled tip, closed bottom; root is bolted.
    ps=[];rs=[]
    for t in np.linspace(0,1,65):
        y=16+40*t;z=-11-7*math.sin(t*math.pi*.8)+4*t**4
        ps.append([1.5*math.sin(t*3),y,z]);rs.append(2.3+4.8*math.sin(math.pi*t)**.65)
    tongue=tube(ps,rs,40).scale((1.6,1,.55))
    # compensate vertical scale so tongue aligns to slider datum
    tongue=tongue.translate((0,0,-5))
    tongue+=box(-6,19,-14,12,12,4)
    tongue-=cyl(0,24,-16,1.65,10)
    # central groove and transverse papillae are actual mesh relief
    grooves=[]
    for t in np.linspace(.23,.9,22):
        y=16+40*t;z=(-11-7*math.sin(t*math.pi*.8)+4*t**4)*.55-5
        w=(2.3+4.8*math.sin(math.pi*t)**.65)*1.6
        grooves.append(tube([[-w*.7,y,z+2],[0,y+.6,z+3.1],[w*.7,y,z+2]],[.55,.7,.55],10))
    tongue+=union(grooves)
    tongue=tongue.translate((0,4,4.4))
    tongue-=box(-30,19,-50,60,18,40.4) # flat bolting saddle, 0.4 mm above carriage
    add('C03','Ribbed curled tongue',tongue,'tongue','tongue',orientation=(180,0,0))

def build_frame():
    # All positions in the head coordinate system: hinge is (0,-40,0).
    frame=box(-57,-66,-19,114,8,38)
    frame+=box(-26,-74,-23.6,52,37,5.6)
    frame-=cyl(0,-59,-25,9,10)
    for x,y in [(-17,-59),(17,-59),(0,-42)]:frame-=cyl(x,y,-25,2.25,12)
    for x in [-49,49]:
        frame+=beamx((-62,3),(20,3),4,x-4,8)
        frame+=cx(x-4,-40,0,7,8)
        frame-=cx(x-5,-40,0,2.2,10)
        frame+=box(x-6,14,3,12,12,16.6)
        frame-=cyl(math.copysign(48,x),20,1,1.7,25)
    frame+=box(-7,-69,3,14,10,16.6);frame-=cyl(0,-64,1,1.7,25)
    # Tongue guide deck, symmetric running clearance 0.5 mm at both sides.
    frame+=box(-13,-59,-20,26,77,3)
    for x in [-13,9]:frame+=box(x,-34,-17,4,52,9)
    for x in [-13,8]:frame+=box(x,-34,-8,5,52,3)
    # MG996R body pocket with tie-down slots: avoids assuming clone tab positions.
    cradle=box(-51,-42,17.5,47,54,3)
    cradle+=box(-51,-42,19,4,54,29)
    cradle+=box(-51,8,19,47,4,29)
    cradle+=box(-51,-42,19,47,4,29)
    cradle-=box(-49,-37,20.5,46,42,29)
    cradle-=cx(-54,-26,31,7.2,8)
    for y in [-32,-2]:cradle-=box(-54,y,19,9,4,24)
    cradle+=box(-49,-62,3,8,24,20)
    frame+=cradle
    frame+=box(0,-61,3,12,12,4)
    frame-=cyl(6,-55,1,1.7,10)
    # A rigid anatomical palate conceals the frame; a slot clears the rod sweep.
    palate=M.cylinder(2.5,1,circular_segments=128).scale((58,52,1)).translate((0,-5,5))
    palate-=box(31,-51,3,14,105,8)
    frame+=palate
    throat=tube([[0,0,-17],[0,0,-29],[0,0,-43],[0,0,-52]],[18,18,14,7],48).scale((1,.2,1)).translate((0,-29.5,0))
    frame+=throat
    for xx in [-14,-7,0,7,14]:
        frame+=tube([[xx,-26.2,-18],[xx*.95,-26.2,-29],[xx*.65,-27.2,-43],[xx*.2,-28,-51]],[.6,.7,.6,.5],12)
    frame-=box(-80,-68,17,55,16,20)+box(25,-68,17,55,16,20)
    add('C04','Head chassis with palate, throat and servo cradle',frame,'gums','head')
    sled=box(-8.5,-45,-16.5,17,81,6.5)
    sled+=box(-5,8,-10,10,10,10)
    sled+=box(-4,10,-2,41,6,4)
    sled+=box(33,10,-11,4,6,13)
    sled+=cx(33,13,-11,5,4)
    sled-=cx(32,13,-11,1.65,6)
    sled-=cyl(0,28,-18,1.65,20)
    add('C05','Tongue carriage with offset connecting-rod lug',sled,'mech','slider',orientation=(180,0,0))
    # identical driven and driving cranks keep the jaw angle equal to servo angle.
    crank=beamx((0,0),(18,0),5,-60,4)-cx(-61,0,0,3.4,6)
    for yy in [7,12]:crank-=cx(-61,yy,0,1.2,6)
    crank-=cx(-61,18,0,1.65,6)
    add('C06','18 mm jaw crank, screwed to supplied servo horn',crank,'mech','servo_crank',orientation=(0,90,0))
    link=beamx((0,0),(14,31),3.8,-69,4)-cx(-70,0,0,1.65,6)-cx(-70,14,31,1.65,6)
    add('C07','34.015 mm jaw parallelogram link',link,'gold','jaw_link',orientation=(0,90,0))
    rod=beamx((0,0),(75,0),3.5,38,4)-cx(37,0,0,1.65,6)-cx(37,75,0,1.65,6)
    add('C08','75 mm tongue connecting rod',rod,'gold','tongue_rod',orientation=(0,90,0))
    rocker=beamx((-40,0),(-40,42),4,28,4)+beamx((-40,0),(-24,-16),4,28,4)
    rocker-=cx(27,-40,0,2.2,6);rocker-=cx(27,-40,42,1.65,6);rocker-=cx(27,-24,-16,1.65,6)
    rocker=rocker.translate((5,0,0))
    # Rocker mounts beside jaw lug with a spacer; source uses x shift in pose.
    add('S01','42 mm jaw-driven tongue rocker',rocker,'gold','single_rocker','one-servo',orientation=(0,90,0))
    mini=box(0,-49,7.6,31,30,3)
    mini+=box(0,-49,7.6,31,2.4,19)+box(0,-22.7,7.6,31,3.7,19)
    for y in [-44,-28]:mini-=box(4,y,7,23,3.5,4)
    mini+=box(0,-57.6,7.9,12,11.6,2.8)
    mini-=cyl(6,-55,6,1.7,8)
    add('D01','MG90S tongue-servo cradle, tie mount',mini,'mech','head','two-servo')
    # The body and horn are specified, rather than a fragile printed servo spline.
    crank2=beamx((0,0),(0,25),4.5,33,4)-cx(32,0,0,2.6,6)
    for zz in [6,10]:crank2-=cx(32,0,zz,1.1,6)
    crank2-=cx(32,0,25,1.65,6)
    add('D02','25 mm tongue crank, screwed to MG90S horn',crank2,'gold','mini_crank','two-servo',orientation=(0,90,0))

def build_base():
    pipe=cyl(0,0,4,75,98,160)+cyl(0,0,0,80,12,160)+cyl(0,0,93,83,20,160)
    pipe-=cyl(0,0,-1,71.5,117,160)
    pipe-=cyl(0,0,103,79.4,12,160)
    # frame aperture and removable display bezel at front (+Y).
    pipe-=box(-27,65,35.5,54,20,31.5)
    for x in [-29,29]:
        pipe+=box(27 if x>0 else -33,66,45,6,9,14);pipe-=cy(x,63,52,1.7,16)
    # underside fasteners and a rear cable entry
    for x,y in [(-48,-40),(48,-40),(0,61)]:
        pipe+=(cyl(x,y,8,7,12)+cyl(x*1.17,y*1.17,8,7,12)).hull();pipe-=cyl(x,y,6,1.7,16)
        pipe-=cyl(x,y,16,3.25,6,6)
    pipe-=box(-7,-80,12,14,20,9)
    lid_holes=[(74.8*math.cos(a),74.8*math.sin(a)) for a in np.radians([45,165,285])]
    for x,y in lid_holes:
        pipe+=cyl(x,y,96,5,7)
        pipe-=cyl(x,y,95,1.7,10);pipe-=cyl(x,y,95,3.25,4,6)
    # weathered shallow casting channels, stay above structural wall minimum
    for a in np.linspace(0,2*np.pi,33)[:-1]:
        pipe-=cyl(75.4*np.cos(a),75.4*np.sin(a),17,.55,71,12)
    add('C09','Warp-pipe enclosure with bottom and top access',pipe,'pipe')
    floor=cyl(0,0,4,71.05,3.6,128)
    for x,y in [(-48,-40),(48,-40),(0,61)]:floor-=cyl(x,y,2,1.7,9)
    for y in [-36,28]:
        for x in [-33,-21,21,33]:floor-=box(x-1.6,y-2,2,3.2,4,9)
    # tie-mounted electronics and ballast bay; no guessed board hole pattern
    floor+=box(-39,-38,7.6,78,2.5,7)+box(-39,33,7.6,78,2.5,7)
    add('C10','Bottom access plate and electronics tie tray',floor,'mech')
    soil=cyl(0,0,103.4,79,4,160)-cyl(0,-18,102,10,8)
    # Low-relief soil particles are printed, all fused to the flat disk.
    rng=np.random.default_rng(11)
    for i in range(220):
        x,y=rng.uniform(-75,75,2)
        if x*x+y*y<74**2 and x*x+(y+18)**2>34**2:
            soil+=sphere((x,y,107.1),rng.uniform(1.1,2.2),(1,1,.55),16)
    for x,y in [(-26,-18),(26,-18),(0,8)]:soil-=cyl(x,y,101,2.25,12)
    for x,y in lid_holes:soil-=cyl(x,y,101,1.7,12)
    # Top lifts out after disconnecting leads and removing three M3 rim screws.
    add('C11','Soil lid and bolted stem seat',soil,'soil')
    ps=[]
    for t in np.linspace(0,1,90):ps.append([3*math.sin(t*4),-18-41*t-8*math.sin(t*math.pi),107+135*t])
    radii=np.linspace(21,16,len(ps))*(1+.04*np.sin(np.linspace(0,8,len(ps))))
    stem=tube(ps,radii,112)-tube(ps,np.full(len(ps),10.),72)
    # long organic ridges follow the stem, 1 mm in actual geometry
    ribs=[]
    for a in np.linspace(0,2*np.pi,15,endpoint=False):
        path=[]
        for j,p in enumerate(ps):
            t=j/(len(ps)-1);ang=a+.28*math.sin(t*6+a)
            path.append(np.array(p)+[radii[j]*math.cos(ang)*.97,radii[j]*math.sin(ang)*.97,0])
        ribs.append(tube(path,np.linspace(1.4,.9,len(ps)),10))
    stem+=union(ribs)
    stem=stem^box(-150,-150,107.8,300,300,131.7)
    stem+=cyl(0,-18,107.8,32,5)-cyl(0,-18,106,10,10)
    stem+=cyl(0,-59,236,25,5)-cyl(0,-59,235,10,10)
    for x,y in [(-26,-18),(26,-18),(0,8)]:stem-=cyl(x,y,105,2.25,12)
    for x,y in [(-17,-59),(17,-59),(0,-42)]:stem-=cyl(x,y,234,2.25,12)
    # leaf sockets: rectangular tenons rather than unsupported decorative contact
    for sg,z,yy in [(-1,162,-40),(1,184,-48)]:
        stem+=box(0 if sg==1 else -30,yy-6,z-5,30,12,10)
        stem-=box(15 if sg==1 else -32,yy-3.3,z-2.3,17,6.6,4.6)
    add('C12','Hollow ribbed stem with cable passage and leaf sockets',stem,'green')
    for id,sg,z,yy in [('C13',-1,162,-40),('C14',1,184,-48)]:
        leaf=make_leaf(sg,z,yy)
        add(id,('Left' if sg<0 else 'Right')+' veined serrated leaf',leaf,'leaf',orientation=(0,0,0))
    bezel=box(-34,75.4,32,68,5,40)-box(-23.2,73,40,46.4,10,23)
    for x in [-29,29]:bezel-=cy(x,70,52,1.7,15)
    # 48 x 30 adjustable PCB shelf supports common TM1637 boards, foam retained
    bezel+=box(-26,59.8,36,3,19,30)+box(23,59.8,36,3,19,30)+box(-26,59.8,36,52,19,3)
    for xx in [-27,22]:bezel-=box(xx,54,43.6,5,12.3,16.8)
    add('C15','Removable clock bezel and adjustable TM1637 pocket',bezel,'gold',orientation=(90,0,0))
    for i,sg in enumerate([-1,1]):
        clamp=box(23 if sg>0 else -33,56.5,44,10,6,16)
        clamp+=box(18 if sg>0 else -27,61.5,44,9,4,16)
        clamp-=cy(sg*29,54,52,1.7,11)
        add('C'+str(16+i),'Display retaining clamp '+str(i+1),clamp,'mech',orientation=(90,0,0))
    coupon=box(0,0,0,50,24,4)
    for x,rad in [(8,1.55),(20,1.65),(33,2.1),(44,2.2)]:coupon-=cyl(x,12,-1,rad,6)
    add('T01','M3 and M4 hole-fit coupon',coupon,'mech',group='test')

def make_leaf(sg,z,yy):
    # Closed sculpted leaf: camber, scalloped margin, thickened root and raised veins.
    nu,nv=65,33;verts=[];fs=[]
    def point(u,v,top=True):
        width=19*math.sin(math.pi*u)**.72*(1+.055*math.sin(u*math.pi*24))+.5
        xx=sg*(31+81*u);y=yy+v*width+23*u*u;zz=z+21*math.sin(u*math.pi*.83)-7*u+3.5*(1-v*v)*math.sin(math.pi*u)
        thick=1.5 if top else -1.5
        return [xx,y,zz+thick]
    for top in [True,False]:
        for i in range(nu):
            for j in range(nv):verts.append(point(i/(nu-1),2*j/(nv-1)-1,top))
    N=nu*nv
    for side in [0,1]:
        for i in range(nu-1):
            for j in range(nv-1):
                a=side*N+i*nv+j;b=a+nv;c=a+1;d=b+1
                fs.extend([[a,b,c],[b,d,c]] if side==0 else [[a,c,b],[b,c,d]])
    boundary=list(range(nv))+[i*nv+nv-1 for i in range(1,nu)]+list(range(N-2,N-nv-1,-1))+[i*nv for i in range(nu-2,0,-1)]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):fs.extend([[a,a+N,b],[b,a+N,b+N]])
    leaf=from_mesh(verts,fs)
    leaf+=tube([point(u,0) for u in np.linspace(0,1,65)],np.linspace(1.6,.6,65),12)
    for u in np.linspace(.15,.83,9):
        for side in [-1,1]:
            pts=[point(u+.1*t,side*.9*t) for t in np.linspace(0,1,12)]
            leaf+=tube(pts,np.linspace(.85,.38,12),10)
    leaf+=box(17 if sg>0 else -29,yy-3,z-2,12,6,4)
    leaf+=box(26 if sg>0 else -34,yy-3,z-2,8,6,4)
    return leaf

def posed(p,q=48,tongue_angle=90,version=2):
    s=p['s'];g=p['group']
    if g in ['jaw','single_rocker']:s=rotate_jaw(s,q)
    elif g in ['slider','tongue']:
        sy,_=slider_position(q if version==1 else tongue_angle,version)
        s=s.translate((0,sy-Y0,0))
    elif g=='servo_crank':s=s.rotate((-q,0,0)).translate((0,-26,31))
    elif g=='jaw_link':
        a=math.radians(q);s=s.translate((0,-40+18*math.cos(a),-18*math.sin(a)))
    elif g=='mini_crank':s=s.rotate((-tongue_angle,0,0)).translate((0,-40,17))
    elif g=='tongue_rod':
        sy,(y,z)=slider_position(q if version==1 else tongue_angle,version)
        ang=math.degrees(math.atan2(-11-z,sy-y));s=s.rotate((ang,0,0)).translate((0,y,z))
    if g in ['head','jaw','single_rocker','slider','tongue','servo_crank','jaw_link','mini_crank','tongue_rod']:s=s.translate((0,0,Z))
    return s

def hardware(version,q=48):
    hs=[('MG996R envelope',box(-46,-36,21.15,36.9,40.7,19.7).translate((0,0,Z)),'black'),
        ('MG996R output shaft reference',cx(-53,-26,Z+31,3,7),'gold'),
        ('MG996R supplied horn envelope',cx(-56,-26,Z+31,10,3),'bone'),
        ('UNO envelope - tie mounted',box(-34,-28,15,68.6,53.4,14),'board'),
        ('DS3231 module envelope',box(-39,-54,17,39,23,12),'board'),
        ('TM1637 module envelope',box(-21,66,40,42,5,24),'black')]
    if version==2:hs.append(('MG90S envelope',box(1.5,-46.1,Z+10.9,28.5,22.8,12.2),'black'))
    # Hardware references are simple envelopes; screws are not claimed exact purchased models.
    for x in [-59,45]:hs.append(('M4 jaw pivot',cx(x,-40,Z,2,14),'gold'))
    return hs

def color_vertices(v,p):
    v=np.array(v,copy=True)
    if p['id']=='C01':v[:,2]-=13
    base=np.array(COLORS[p['color']],float);colors=np.tile(base,(len(v),1));id=p['id']
    if id in ['C01','C02']:
        rx=76 if id=='C01' else 72;zc=10 if id=='C01' else 0
        radial=np.sqrt((v[:,0]*(76/82 if id=='C01' else 1))**2+v[:,1]**2)
        lipmask=(np.abs(radial-rx)<6.4)&(np.abs(v[:,2]-zc)<5.5)
        colors[lipmask]=[180,145,122]
        fang=(v[:,2]<(5 if id=='C01' else 14))&(v[:,2]>(-15 if id=='C01' else -2))&(radial<rx-1)&(radial>rx-14)
        colors[fang]=[218,201,158]
        interior=(v[:,0]/(84 if id=='C01' else 74))**2+(v[:,1]/(78 if id=='C01' else 74))**2+((v[:,2]-zc)/(68 if id=='C01' else 48))**2<.93
        colors[interior&~lipmask&~fang]=[82,31,38]
        if id=='C01':
            for c,n in json.loads((ROOT/'validation'/'spot_centers.json').read_text()):
                dist=np.linalg.norm(v-np.asarray(c),axis=1)
                w=np.clip((9.0-dist)/1.2,0,1)*(~interior)
                colors=colors*(1-w[:,None])+np.array([214,204,175])*w[:,None]
    noise=1+.035*np.sin(v[:,0]*1.31+np.sin(v[:,1]*.8))*np.sin(v[:,2]*1.7)
    return np.clip(colors*noise[:,None],0,255).astype(np.uint8)

def rhmesh(s,p=None):
    v,f=meshdata(s);o=r.Mesh();o.Vertices.UseDoublePrecisionVertices=True
    for a in v:o.Vertices.AddPoint3d(*map(float,a))
    for a in f:o.Faces.AddFace(*map(int,a))
    if p:
        original_v,original_f=meshdata(p['s'])
        if len(original_v)==len(v) and np.array_equal(original_f,f):
            for c in color_vertices(original_v,p):o.VertexColors.Add(*map(int,c))
    o.Normals.ComputeNormals();o.Compact()
    assert o.IsValid and o.IsClosed
    return o

def export():
    report=[];cache={};manifest=[]
    for p in PARTS.values():
        s=p['s'];v,f=meshdata(s)
        cache[p['id']+'_v']=v;cache[p['id']+'_f']=f;cache[p['id']+'_c']=color_vertices(v,p)
        pp=s.rotate(p['orientation']);bb=pp.bounding_box();pp=pp.translate((-bb[0],-bb[1],-bb[2]));bb=pp.bounding_box()
        assert bb[3]<230 and bb[4]<230,(p['id'],bb)
        vv,ff=meshdata(pp);tm=trimesh.Trimesh(vv,ff,process=False)
        assert tm.is_watertight and tm.is_winding_consistent
        path=ROOT/'stl'/p['variant']/(p['id']+'_'+p['name'].lower().replace(' ','_').replace(',','').replace('/','-')+'.stl')
        path.parent.mkdir(exist_ok=True,parents=True);tm.export(path)
        row=dict(id=p['id'],name=p['name'],variant=p['variant'],size_mm=[round(bb[3],2),round(bb[4],2),round(bb[5],2)],volume_cm3=round(s.volume()/1000,2),triangles=len(f),watertight=True,components=1,stl=str(path.relative_to(ROOT)).replace('\\','/'),orientation=list(p['orientation']),group=p['group'],color=p['color'])
        report.append(row);manifest.append(row)
    np.savez_compressed(ROOT/'validation'/'geometry_cache.npz',**cache)
    active={str((ROOT/p['stl']).resolve()) for p in report}
    for old in (ROOT/'stl').rglob('*.stl'):
        if str(old.resolve()) not in active:old.unlink()
    (ROOT/'validation'/'parts.json').write_text(json.dumps(manifest,indent=2))
    with (ROOT/'docs'/'print_parts.csv').open('w',newline='') as h:
        writer=csv.writer(h);writer.writerow(['Part','Name','Version','X mm','Y mm','Z mm','Volume cm3','STL'])
        for p in report:writer.writerow([p['id'],p['name'],p['variant'],*p['size_mm'],p['volume_cm3'],p['stl']])
    for version in [1,2]:
        doc=r.File3dm();doc.Settings.ModelUnitSystem=r.UnitSystem.Millimeters;doc.Settings.ModelAbsoluteTolerance=.01
        layers={}
        def layer(name,color,visible=True):
            a=r.Layer();a.Name=name;a.Color=(*color,255);a.Visible=visible;ix=doc.Layers.Add(a);layers[name]=ix;return ix
        ass=layer('01 ASSEMBLED - open cuckoo pose',(130,62,53));hard=layer('02 HARDWARE ENVELOPES - DO NOT PRINT',(66,83,81))
        closed=layer('03 CLOSED POSE - alternative view',(130,62,53),False)
        mech=layer('04 MECHANISM ONLY - at X 300 mm',(80,85,82),False)
        notes=layer('80 DESIGN NOTES - not printable',(200,200,200),False)
        guides=layer('90 CONSTRUCTION CURVES - not printable',(90,130,170),False)
        mats={}
        for c,rgb in COLORS.items():
            mat=r.Material();mat.Name=c;mat.DiffuseColor=(*rgb,255);mat.Shine=35 if c in ['red','tongue'] else 8;mats[c]=doc.Materials.Add(mat)
        def put(s,name,ly,p=None):
            a=r.ObjectAttributes();a.Name=name;a.LayerIndex=ly
            if p:
                a.MaterialIndex=mats[p['color']];a.MaterialSource=r.ObjectMaterialSource.MaterialFromObject
                a.ObjectColor=(*COLORS[p['color']],255);a.ColorSource=r.ObjectColorSource.ColorFromObject
                a.SetUserString('Part_ID',p['id']);a.SetUserString('Print_source',next(i['stl'] for i in manifest if i['id']==p['id']))
            doc.Objects.AddMesh(rhmesh(s,p),a)
        selected=[p for p in PARTS.values() if p['variant'] in ['common',('one-servo' if version==1 else 'two-servo')] and p['group']!='test']
        for p in selected:
            put(posed(p,version=version),p['id']+' | '+p['name'],ass,p)
            put(posed(p,q=0,tongue_angle=0,version=version),p['id']+' | CLOSED',closed,p)
            if p['group'] in ['head','jaw','single_rocker','slider','servo_crank','jaw_link','mini_crank','tongue_rod','tongue'] and p['id'] not in ['C01','C02']:
                put(posed(p,version=version).translate((300,0,0)),p['id']+' | mechanism',mech,p)
        for name,s,c in hardware(version):put(s,name,hard)
        # Independently oriented plates, one clearly labelled printable part per plate.
        for i,p in enumerate(selected+[PARTS['T01']]):
            ly=layer('PRINT '+p['id']+' - '+p['name'],COLORS[p['color']],False)
            s=p['s'].rotate(p['orientation']);bb=s.bounding_box();s=s.translate((10-bb[0]+(i%5)*260,10-bb[1]+(i//5)*260-1400,-bb[2]))
            put(s,p['id']+' | PRINT THIS ONE',ly,p)
            a=r.ObjectAttributes();a.LayerIndex=ly
            xx=(i%5)*260;yy=(i//5)*260-1400
            doc.Objects.AddPolyline([r.Point3d(xx,yy,0),r.Point3d(xx+240,yy,0),r.Point3d(xx+240,yy+240,0),r.Point3d(xx,yy+240,0),r.Point3d(xx,yy,0)],a)
        a=r.ObjectAttributes();a.LayerIndex=notes
        text=('PIRANHA CLOCK / '+str(version)+' SERVO / mm\n'+
              'Prototype: digitally checked, not physically built.\n'+
              'C01/C02 skin, veins, plaques and lip folds are real geometry.\n'+
              'Organic parts are editable closed meshes. Source generator included.\n'+
              'Use PRINT layers or STLs; assembly includes overlapping reference hardware.\n'+
              'Bed 240 x 240 mm; all part footprints < 230 x 230 mm.\n'+
              'Read docs/ASSEMBLY.md and validation/report.json before printing.\n'+
              'Jaw 0-48 deg. Tongue rod 75 mm. 42 mm linked rocker or 25 mm independent crank.\n'+
              'Print coupon and mechanism before detailed shells. Calibrate actual servo horns.')
        doc.Objects.AddTextDot(text,r.Point3d(170,0,150),a)
        a=r.ObjectAttributes();a.LayerIndex=guides
        doc.Objects.AddLine(r.Point3d(-80,-40,Z),r.Point3d(80,-40,Z),a)
        doc.Objects.AddLine(r.Point3d(0,-34,Z-13),r.Point3d(0,75,Z-13),a)
        doc.Strings['Design_status']='Prototype; geometric validation is not a physical mechanism test.'
        doc.Strings['Version']=str(version)+' servo'
        view=r.ViewInfo();view.Name='Assembled perspective'
        view.Viewport.SetCameraLocation(r.Point3d(390,650,370))
        view.Viewport.SetCameraDirection(r.Vector3d(-390,-650,-192))
        view.Viewport.SetCameraUp(r.Vector3d(0,0,1))
        view.Viewport.TargetPoint=r.Point3d(0,0,178)
        view.Viewport.ChangeToParallelProjection(True)
        view.Viewport.SetFrustum(-180,180,-205,205,1,2000)
        doc.Views.Add(view);doc.NamedViews.Add(view)
        path=ROOT/'cad'/('Piranha_Clock_'+('One_Servo' if version==1 else 'Two_Servos')+'.3dm')
        assert doc.Write(str(path),7)
        re=r.File3dm.Read(str(path));meshes=[o.Geometry for o in re.Objects if isinstance(o.Geometry,r.Mesh)]
        assert all(g.IsValid and g.IsClosed for g in meshes)
        print('RHINO_REOPEN_OK',path.name,len(meshes),flush=True)
    out=dict(units='mm',bed_mm=[240,240],printable_parts=report,physical_tested=False)
    (ROOT/'validation'/'report.json').write_text(json.dumps(out,indent=2))

if __name__=='__main__':
    build_organic();build_frame();build_base();export()
