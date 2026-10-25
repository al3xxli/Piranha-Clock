"""V6: press-fit clock, captive tongue, flat teeth and user-cut pot sleeve.
All dimensions mm. Kinematic poses assume equal joint angles, not elastic FEA.
"""
from pathlib import Path
import json,math,csv,itertools
import numpy as np
import trimesh
import base_geometry as b
from base_geometry import box,cyl,cx,cy,sphere,union,tube,beamx,meshdata,add
ROOT=Path(__file__).resolve().parents[1]
b.ROOT=ROOT
PITCH=22.; COUNT=7; ROOT_PT=np.array([7.,15.,11.]); ROOT_ANGLE=8.
UPPER_OPEN=50.; GEAR_RATIO=4.; U=np.array([0.,-50.,8.]); L=np.array([0.,-50.,-32.])
import mouth_geometry as mouth
b.color_vertices=mouth.colors
MAX_CURL=45.; SPOOL_R=10.
PRINT_CURL=22.5  # Hinge axes remain vertical; stop tabs print between limits.
PARTS=b.PARTS

def section_matrix(i,curl):
    p=ROOT_PT.copy()
    for j in range(i):
        a=math.radians(ROOT_ANGLE+j*curl)
        p+=np.array([0,PITCH*math.cos(a),PITCH*math.sin(a)])
    a=math.radians(ROOT_ANGLE+i*curl)
    return np.array([[1,0,0,p[0]],[0,math.cos(a),-math.sin(a),p[1]],[0,math.sin(a),math.cos(a),p[2]]])

def point(i,curl,xyz):
    t=section_matrix(i,curl);return t[:,:3]@np.array(xyz)+t[:,3]

def route(curl,top=False):
    z=5.8 if top else -6.0
    return np.array([point(i,curl,[0,y,z]) for i in range(COUNT) for y in [5.,17.]])

def tendon_length(curl):
    return float(np.linalg.norm(np.diff(route(curl),axis=0),axis=1).sum())

def takeup(curl):return tendon_length(MAX_CURL)-tendon_length(curl)

def curl_for_fraction(f):
    low,high=0.,45.;target=max(0.,min(1.,f))*takeup(0)
    for _ in range(36):
        mid=(low+high)/2
        if takeup(mid)>target:low=mid
        else:high=mid
    return (low+high)/2

def arc_wedge(y,z,r0,r1,a0,a1,x,th):
    angles=np.radians(np.linspace(a0,a1,max(3,int(abs(a1-a0)/3)+1)))
    pts=np.array([[y+r1*np.cos(a),z+r1*np.sin(a)] for a in angles]+[[y+r0*np.cos(a),z+r0*np.sin(a)] for a in angles[::-1]])
    return b.m.CrossSection([pts]).extrude(th).rotate((90,0,90)).translate((x,0,0))

def reuse_base():
    old=ROOT.parent/'validation'
    import sys
    if '--from-base-cache' in sys.argv and (old/'geometry_cache.npz').exists():
        data=np.load(old/'geometry_cache.npz')
        for p in json.loads((old/'parts.json').read_text()):
            if p['id'] not in ['C09','C10','C11','C12','C13','C14','C15','C16','C17','T01']:continue
            p['s']=b.M(b.m.Mesh64(data[p['id']+'_v'],data[p['id']+'_f'].astype(np.uint64)));PARTS[p['id']]=p
    else:b.build_base()
    mouth.organic();mouth.mechanism()

def make_section(i):
    width=[36,36,34,32,29,25,20][i]
    # Flattened, tapered flesh with physically raised taste papillae.
    body=sphere((0,11,0.3),1,(width/2,7,4.2),64)
    body+=box(-5,3,-2.4,10,17,4.8)
    for y in [7.,10.,13.,16.]:
        w=width*.34*math.sqrt(max(.1,1-((y-11)/7)**2))
        body+=tube([[-w,y,2.4],[0,y+.45,4.1],[w,y,2.4]],[.65,.75,.65],12)
    rng=np.random.default_rng(70+i)
    for _ in range(26):
        x,y=rng.uniform(-width*.34,width*.34),rng.uniform(6.5,15.5)
        z=.3+4.2*math.sqrt(max(.01,1-(x/(width/2))**2-((y-11)/7)**2))
        body+=sphere((x,y,z-.12),.55,(1,1,.75),12)
    # Clear the fork swept volume from the flesh at the preceding end.
    if i<COUNT-1:
        body-=cx(-25,PITCH,0,6.35,16.1)+cx(8.9,PITCH,0,6.35,16.1)
    h=b.M()
    # Fork at proximal joint, single central barrel at distal joint.
    if i>0:
        for x in [-13,9]:h+=cx(x,0,0,6,4)
        h+=box(-13,2,-2.3,26,5,4.6)
        h-=cx(-14,0,0,1.2,28)
        # Sector recess gives exact 0 and 45 degree stops on the left fork.
        h-=arc_wedge(0,0,2.3,6.6,-145,-80,-13.1,4.2)
    if i<COUNT-1:
        h+=cx(-8.6,PITCH,0,3.05,17.2)
        h+=box(-8.6,16,-2.3,17.2,6,4.6)
        h+=arc_wedge(PITCH,0,2.5,6.,-100,-80,-12.6,11.6)
        h-=cx(-14,PITCH,0,1.2,28)
    else:
        body+=sphere((0,20,0),1,(7,6,3.0),48)
    body+=h
    if i>0:body-=cx(-8.9,0,0,3.8,17.8)
    # Underside string straightens the upward curl; top elastic links return it.
    for zz,rr in [(-6.0,.8),(5.8,1.1)]:
        body+=cy(0,4.4,zz,rr+1.05,13.2)
        body+=box(-2.1,5, min(zz,0),4.2,12,abs(zz)+.1)
        body-=cy(0,3.8,zz,rr,14.4)
    # Straight dorsal groove splits papillae and makes the cord serviceable.
    if i==0:
        body=body.transform(section_matrix(0,MAX_CURL))
        plate=box(-24,8,-8.6,10,19,3.3)+box(34,8,-8.6,8.5,19,3.3)
        plate+=box(-20,16,-5.4,6,7,12)+box(34,16,-5.4,6,7,12)
        plate+=box(-20,18,3,60,5,3.8)
        plate+=(box(-5,20,4,30,3,2)+(body^box(-6,20,3,32,8,15))).hull()
        body+=plate
        for xx in [-19,39]:body-=cyl(xx,12,-11,1.7,12)
        for zz,rr in [(-6.0,.8),(5.8,1.1)]:body-=cy(0,-6,zz,rr,24.4).transform(section_matrix(0,MAX_CURL))
        body-=tube([[35,-1,-3],point(0,MAX_CURL,[0,5,-6.0]),point(0,MAX_CURL,[0,17,-6.0])],1.1,24)
        add('A01','Upward curl tongue root on lower jaw',body,'tongue','lower')
    else:add('A'+str(i+1).zfill(2),'Tongue section '+str(i+1)+' of 7',body,'tongue','section',orientation=(0,90,0))


def build_legacy():
    reuse_base()
    for i in range(COUNT):make_section(i)
    yy,zz=-13.,-19.8
    spool=cx(33,yy,zz,9.75,4)+cx(32,yy,zz,11.5,1)+cx(37,yy,zz,11.5,1)
    spool-=cx(31,yy,zz,2.6,9)
    for d in [-6,6]:spool-=cx(31,yy,zz+d,1.1,9)
    spool-=cx(31,yy+8,zz,1.,9)
    add('A08','MG90S tendon drum 20 mm pitch diameter',spool,'gold','spool',orientation=(0,90,0))
    guide=box(31,-6,-8.6,12,10,3)+sphere((35,-1,-3),3.3,n=32)
    guide+=box(32,-4,-6,6,6,3)
    guide-=tube([[35,-18,-11],[35,-1,-3],point(0,45,[0,5,-6.0])],1.3,24)
    guide-=cyl(41,1,-10,1.7,10)
    add('A09','Lower jaw tendon fairlead',guide,'mech','lower')
    jaw=PARTS['C02']['s']+box(31,-6,-13,14,12,4)
    jaw-=cx(31.5,-13,-19.8,12.3,7.5)
    for xx in [-19,39]:jaw-=cyl(xx,12,-15,1.7,12)
    jaw-=cyl(41,1,-15,1.7,12);PARTS['C02']['s']=jaw
    fit=box(0,0,0,48,24,4)
    for x,rr in [(7,1.1),(17,1.2),(29,.8),(40,1.1)]:fit-=cyl(x,12,-1,rr,6)
    add('A10','2 mm pin and tendon fit coupon',fit,'mech','test')

def jaw_pose(s,q,upper=False):
    pivot=U if upper else L
    return s.translate(-pivot).rotate((q if upper else -q/GEAR_RATIO,0,0)).translate(pivot)

def posed(p,q=50,curl=0):
    s=p['s'];g=p['group']
    if g=='fixed' or g=='test':return s
    if g=='section':s=s.transform(section_matrix(p.get('section_index',int(p['id'][1:])-1),curl));s=jaw_pose(s,q)
    elif g=='spool':
        deg=math.degrees(takeup(curl)/SPOOL_R)
        s=s.translate((0,13,19.8)).rotate((deg,0,0)).translate((0,-13,-19.8));s=jaw_pose(s,q)
    elif g in ['upper','lower']:s=jaw_pose(s,q,g=='upper')
    return s.translate((0,0,b.Z))

def hardware(q=50,curl=0):
    hs=[('MG995 case envelope',box(-27,-60,-1.85,36.9,40.7,19.7),'black'),
        ('MG995 output shaft reference',cx(-31,-50,8,3,4),'gold'),
        ('MG995 purchased horn reference',cx(-37,-50,8,10,3),'bone'),
        ('Upper right M4 pivot',cx(45,-50,8,2,16),'gold')]
    hs.append(('Lower left M4 pivot',cx(-51.9,-50,-32,2,30),'gold'))
    hs.append(('Lower right M4 pivot',cx(45,-50,-32,2,19),'gold'))
    hs.append(('Envelope left M4 button head',cx(-54.4,-50,-32,4,2.5),'gold'))
    for y,z in [(-71,-20),(-68,-40)]:
        hs.append(('Envelope cheek M3 screw',cx(-57,y,z,1.5,30)+cx(-58.8,y,z,2.9,1.8),'gold'))
        hs.append(('Envelope cheek M3 nut',cx(-30,y,z,3.175,2.4,6),'gold'))
    for a in np.radians([0,120,240]):
        y=-50+10*np.cos(a);z=-32+10*np.sin(a)
        bolt=cx(-50.6,y,z,1.5,12)+cx(-52.4,y,z,2.9,1.8)
        nut=cx(-41.8,y,z,3.175,2.4,6)
        hs.append(('Envelope lower gear M3 screw',jaw_pose(bolt,q),'gold'))
        hs.append(('Envelope lower gear M3 nut',jaw_pose(nut,q),'gold'))
    for dz in [-4.8,4.8]:
        bolt=cx(-51.4,-50,8+dz,1.,20)+cx(-53.4,-50,8+dz,1.9,2)
        nut=cx(-34,-50,8+dz,2.3,1.6,6)
        hs.append(('Envelope upper gear M2 screw',jaw_pose(bolt,q,True),'gold'))
        hs.append(('Envelope upper gear M2 nut',jaw_pose(nut,q,True),'gold'))
    hs=[(nm,s.translate((0,0,b.Z)),c) for nm,s,c in hs]
    moving=[('MG90S case envelope',box(1.5,-19.1,-25.9,28.5,22.8,12.2),'black'),
        ('MG90S shaft reference',cx(30,-13,-19.8,2.5,4.5),'gold'),
        ('MG90S purchased horn reference',cx(30.5,-13,-19.8,8,1.4),'bone')]
    for i in range(1,COUNT):
        pt=point(i,curl,[0,0,0]);moving.append(('Tongue steel pin '+str(i),cx(pt[0]-14,pt[1],pt[2],1,28),'gold'))
    hs += [(nm,jaw_pose(s,q).translate((0,0,b.Z)),c) for nm,s,c in moving]
    for nm,s,c in b.hardware(2):
        if not ('MG' in nm or 'pivot' in nm):hs.append((nm,s,c))
    return hs

def cords(curl,q=50):
    out=[]
    for top,c in [(False,'gold'),(True,'bone')]:
        ps=route(curl,top)
        if not top:
            d=np.array([12.,16.8]);dd=float(d@d)
            tan=SPOOL_R*SPOOL_R/dd*d+SPOOL_R*math.sqrt(dd-SPOOL_R*SPOOL_R)/dd*np.array([-d[1],d[0]])
            ps=np.vstack([[39,-13+tan[0],-19.8+tan[1]],[39,-1,-3],ps])
        s=tube(ps,.65 if top else .25,10);s=jaw_pose(s,q).translate((0,0,b.Z))
        out.append(('Elastic return' if top else 'Pull tendon',s,c))
    return out


def print_solid(p):
    s=p['s']
    if p.get('print_assembly') in ['PIP_TONGUE','PIP_TEST']:
        i=p.get('section_index',0) if p['print_assembly']=='PIP_TONGUE' else (0 if p['id']=='T04' else 1)
        angle=i*PRINT_CURL
        position=np.array([0.,0.,0.])
        for j in range(i):
            a=math.radians(j*PRINT_CURL)
            position+=np.array([0.,PITCH*math.cos(a),PITCH*math.sin(a)])
        return s.rotate((angle,0,0)).translate(position).rotate((0,-90,0))
    if 'flat_pin_axis' in p:
        inverse={'X':(0,-90,0),'Y':(90,0,0),'NZ':(180,0,0),'Z':(0,0,0)}[p['flat_pin_axis']]
        return s.rotate(inverse).rotate((90,0,0))
    if 'flat_tooth_angle_deg' in p:
        return s.rotate((0,0,-p['flat_tooth_angle_deg'])).rotate((90,0,0))
    return s.rotate(p['orientation'])

def save():
    from layout_print_beds import checked_stl_part
    manifest=[];cache={}
    for p in PARTS.values():
        s=p['s'];vv,ff=meshdata(s)
        tm=trimesh.Trimesh(vv,ff,process=False)
        positive=[x for x in s.decompose() if x.volume()>1e-6]
        assert tm.is_watertight and tm.is_winding_consistent and len(positive)==1,(p['id'],len(positive))
        cache[p['id']+'_v']=vv;cache[p['id']+'_f']=ff
        pr=print_solid(p);bb=pr.bounding_box();print_min=list(bb[:3]);pr=pr.translate((-bb[0],-bb[1],-bb[2]));bb=pr.bounding_box()
        assert bb[3]<240 and bb[4]<240
        v,f=meshdata(pr);path=ROOT/'stl'/(p['id']+'.stl');path.parent.mkdir(exist_ok=True)
        export_mesh,export_cleanup=checked_stl_part(trimesh.Trimesh(v,f,process=False))
        export_mesh.export(path)
        d={k:v for k,v in p.items() if k!='s'}
        d.update(print_bbox_min_mm=print_min,size_mm=[round(x,3) for x in bb[3:]],volume_cm3=s.volume()/1000,stl='stl/'+p['id']+'.stl',triangles=len(ff),watertight=True,stl_cleanup_tolerance_mm=export_cleanup,stl_triangles=len(export_mesh.faces))
        manifest.append(d)
    composites=[('Tongue_Print_in_Place',[f'A{i:02}' for i in range(1,8)],[22*(i-1) for i in range(1,8)]),('Hinge_Sample_Print_in_Place',['T04','T05'],[0,22])]
    for name,ids,ys in composites:
        solids=[print_solid(PARTS[id]) for id in ids]
        bb=np.min(np.array([x.bounding_box()[:3] for x in solids]),axis=0)
        meshes=[]
        for solid in solids:
            vv,ff=meshdata(solid.translate(-bb));mesh,_=checked_stl_part(trimesh.Trimesh(vv,ff,process=False));meshes.append(mesh)
        path=ROOT/'stl'/(name+'.stl');trimesh.util.concatenate(meshes).export(path)
        rb=trimesh.load_mesh(path,process=True);assert len(rb.split(only_watertight=False))==len(ids) and rb.is_watertight
        for row in manifest:
            if row['id'] in ids:
                row['stl']='stl/'+name+'.stl';(ROOT/'stl'/(row['id']+'.stl')).unlink(missing_ok=True)
    for old in (ROOT/'stl').glob('*.stl'):

        if old.stem not in PARTS and old.stem not in [x[0] for x in composites]:old.unlink()
    np.savez_compressed(ROOT/'validation'/'geometry_cache.npz',**cache)
    (ROOT/'validation'/'parts.json').write_text(json.dumps(manifest,indent=2))
    with (ROOT/'docs'/'print_parts.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['ID','Part','X mm','Y mm','Z mm','STL'])
        for p in manifest:w.writerow([p['id'],p['name'],*p['size_mm'],p['stl']])
    r=b.r;doc=r.File3dm();doc.Settings.ModelUnitSystem=r.UnitSystem.Millimeters;doc.Settings.ModelAbsoluteTolerance=.01
    materials={}
    for name,rgb in b.COLORS.items():
        mat=r.Material();mat.Name=name;mat.DiffuseColor=(*rgb,255);mat.Shine=30 if name in ['red','jaw','tongue'] else 8
        materials[name]=doc.Materials.Add(mat)
    def layer(name,visible=True):
        l=r.Layer();l.Name=name;l.Visible=visible;return doc.Layers.Add(l)
    def put(s,name,li,p=None,col=None):
        a=r.ObjectAttributes();a.LayerIndex=li;a.Name=name
        color_name=col or (p['color'] if p else 'mech');c=b.COLORS[color_name];a.ObjectColor=(*c,255);a.ColorSource=r.ObjectColorSource.ColorFromObject
        a.MaterialIndex=materials[color_name];a.MaterialSource=r.ObjectMaterialSource.MaterialFromObject
        if p:
            a.SetUserString('Part ID',p['id'])
            a.SetUserString('Print file',next(x['stl'] for x in manifest if x['id']==p['id']))
        doc.Objects.AddMesh(b.rhmesh(s,p),a)
    poses=[('01 ASSEMBLED - tongue extended',50,0,(0,0,0),True),('03 RESTING - curled in mouth',0,45,(300,0,0),False),('04 MECHANISM - shell removed',50,22.5,(600,0,0),False)]
    for name,q,curl,offset,vis in poses:
        li=layer(name,vis)
        for p in PARTS.values():
            if p['group']=='test':continue
            if name.startswith('04') and (p['id'].startswith('U') or p['id'] in ['C01','C18','C09','C10','C11','C12','C13','C14','C15','C16','C17']):continue
            put(posed(p,q,curl).translate(offset),p['id']+' | '+p['name'],li,p)
        hi=layer(name+' - purchased hardware and cords',vis)
        for nm,s,c in hardware(q,curl)+cords(curl,q):put(s.translate(offset),nm+' | DO NOT PRINT',hi,col=c)
    li=layer('05 TEETH - exploded insertion',False)
    for p in PARTS.values():
        if p['id'] not in ['C01','C02'] and not p['id'].startswith(('U','L')):continue
        ep=dict(p)
        if p['id'].startswith(('U','L')):ep['s']=p['s'].translate((0,0,-20 if p['group']=='upper' else 20))
        put(posed(ep,50,45).translate((950,0,0)),p['id']+' | EXPLODED REFERENCE',li,p)
    for i,p in enumerate(PARTS.values()):
        li=layer('PRINT '+p['id']+' - '+p['name'],False);s=print_solid(p);bb=s.bounding_box()
        s=s.translate((i%5*260+10-bb[0],i//5*260-1700+10-bb[1],-bb[2]));put(s,p['id']+' | PRINT',li,p)
    ni=layer('80 NOTES - prototype',False);a=r.ObjectAttributes();a.LayerIndex=ni
    doc.Objects.AddTextDot('V6 PRESS FIT + LIGHTWEIGHT / mm\n14 flat snap-in teeth; custom spline inserts\nMG995 drives upper +50 deg, lower -12.5 deg\nCaptive print-in-place tongue; MG90S in lower jaw\nUse the separate PRINT BEDS model for batch exports\nPrototype: fit and strength require physical testing.',r.Point3d(170,0,180),a)
    view=r.ViewInfo();view.Name='Extended tongue';view.Viewport.SetCameraLocation(r.Point3d(390,700,405));view.Viewport.SetCameraDirection(r.Vector3d(-390,-676,-200));view.Viewport.SetCameraUp(r.Vector3d(0,0,1));view.Viewport.TargetPoint=r.Point3d(0,24,205);view.Viewport.ChangeToParallelProjection(True);view.Viewport.SetFrustum(-235,235,-235,235,1,2200);doc.Views.Add(view);doc.NamedViews.Add(view)
    ev=r.ViewInfo();ev.Name='Teeth - exploded insertion';ev.Viewport.SetCameraLocation(r.Point3d(1240,500,405));ev.Viewport.SetCameraDirection(r.Vector3d(-290,-470,-115));ev.Viewport.SetCameraUp(r.Vector3d(0,0,1));ev.Viewport.TargetPoint=r.Point3d(950,30,290);ev.Viewport.ChangeToParallelProjection(True);ev.Viewport.SetFrustum(-140,140,-140,140,1,2000);doc.NamedViews.Add(ev)
    path=ROOT/'cad'/'Piranha_Clock_V6_Press_Fit.3dm';assert doc.Write(str(path),7)
    read=r.File3dm.Read(str(path));meshes=[o.Geometry for o in read.Objects if isinstance(o.Geometry,r.Mesh)];assert all(m.IsValid and m.IsClosed for m in meshes)
    report=dict(parts=len(manifest),rhino_closed_valid_meshes=len(meshes),units='mm',bed_mm=[240,240],tongue_pitch_length_mm=COUNT*PITCH,take_up_mm=takeup(0),spool_sweep_deg=math.degrees(takeup(0)/SPOOL_R),physical_tested=False)
    (ROOT/'validation'/'geometry.json').write_text(json.dumps(report,indent=2));print(report,flush=True)

def load():
    data=np.load(ROOT/'validation'/'geometry_cache.npz')
    for p in json.loads((ROOT/'validation'/'parts.json').read_text()):
        p['s']=b.M(b.m.Mesh64(data[p['id']+'_v'],data[p['id']+'_f'].astype(np.uint64)));PARTS[p['id']]=p

def build():
    import press_fit as pf
    # Rebuildable from source; use cached V5 during development only if requested.
    import sys
    if '--from-v5-cache' in sys.argv:
        old=ROOT.parent/'v5-replaceable-teeth'/'validation'
        data=np.load(old/'geometry_cache.npz')
        for p in json.loads((old/'parts.json').read_text(encoding='utf-8')):
            p['s']=b.M(b.m.Mesh64(data[p['id']+'_v'],data[p['id']+'_f'].astype(np.uint64)));PARTS[p['id']]=p
    else:build_legacy()
    pf.revise()

# Purchased hardware excludes user-installed screws, pins, nuts and cable ties.
def hardware(q=50,curl=0):
    hs=[('MG995 case envelope',box(-27,-60,-1.85,36.9,40.7,19.7),'black'),
        ('MG995 output shaft reference',cx(-31,-50,8,3,4),'gold')]
    hs=[(nm,s.translate((0,0,b.Z)),c) for nm,s,c in hs]
    moving=[('MG90S case envelope',box(1.5,-19.1,-25.9,28.5,22.8,12.2),'black'),
        ('MG90S shaft reference',cx(30,-13,-19.8,2.5,4.5),'gold')]
    hs += [(nm,jaw_pose(s,q).translate((0,0,b.Z)),c) for nm,s,c in moving]
    for nm,s,c in b.hardware(2):
        if any(k in nm for k in ['UNO','DS3231','TM1637']):hs.append((nm.replace('tie mounted','envelope'),s,c))
    # Cardboard is reference geometry, excluded from printable parts.
    sleeve=cyl(0,0,3,77,98,160)-cyl(0,0,2,76,100,160)
    sleeve-=box(-27,65,35.5,54,20,31.5)
    for xx in [-29,29]:sleeve-=cy(xx,63,52,2.2,20)
    hs.append(('USER CUT sleeve - 1 mm cardboard reference',sleeve,'soil'))
    return hs

if __name__=='__main__':build();save()

