"""Create eight Rhino print-bed layers and matching bed-local STL exports.

Uses the closed, vertex-colored PRINT meshes in the V6 assembly model. All
operations on parts are rigid transforms; sculpted geometry is not remeshed.
The source model and original individual STLs are never modified.
"""
from pathlib import Path
import csv
import hashlib
import io
import json
import math

import numpy as np
import rhino3dm as r
import trimesh
import manifold3d

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'cad/Piranha_Clock_V6_Press_Fit.3dm'
OUTPUT = ROOT / 'cad/Piranha_Clock_V6_Print_Beds.3dm'
EDGE = 10.0
GAP = 3.0  # Retain the user's nested bezel/clamp arrangement with >3 mm gap.

# Rotations relative to the original individual PRINT mesh, then lower-left XY.
# Coordinates below are local to a 240 x 240 mm build plate.
BEDS = [
    dict(name='Fit samples, flat pins and cheek',slug='Cheek_PushPins',parts=[
        ('T01',(0,0,0),(15,15)),('T03',(0,0,0),(85,15)),('T02',(0,0,90),(150,15)),
        ('T04',(0,0,0),(100,175)),('T05',(0,0,0),(100,175)),
        *[(f'R{i:02}',(0,0,90),(10+36*((i-1)%6),105+13*((i-1)//6))) for i in range(1,29)],
        *[(f'F{g}{i}',(0,0,0),(15+25*(i-1),55+25*(g-1))) for g in [1,2] for i in range(1,7)],
        ('C18',(180,0,0),(15,175)),
    ]),
    dict(name='Upright hinges, drive and open tray',slug='PIP_Tongue_and_Drive',parts=[
        *[(f'A{i:02}',(0,0,0),(15,15)) for i in range(1,8)],
        ('A00',(0,0,0),(145,15)),('G02',(180,0,0),(170,55)),
        ('A08',(0,0,0),(140,60)),('A09',(0,0,0),(140,90)),
        ('H01',(0,0,0),(15,130)),('H02',(0,0,0),(40,130)),
        ('S01',(0,0,90),(15,160)),('S02',(0,0,0),(50,175)),
        ('D01',(0,0,0),(65,130)),('D02',(0,0,0),(82,130)),
        ('C10',(0,0,90),(105,120)),
    ]),
    dict(name='Stem and structural mounts',slug='Stem_and_Mounts',parts=[
        ('G00',(180,0,0),(23.8255,25.4039)),('C04',(-90,0,-90),(150.3647,26.1795)),('C12',(0,0,90),(70.2903,139.9387)),
        ('C15',(180,0,0),(47.745,45.37)),('C16',(0,0,0),(63.92,56.94)),('C17',(0,0,0),(84.15,56.94))]),
    dict(name='Open top support and leaves',slug='Top_Support_and_Leaves',parts=[
        ('C11',(0,0,0),(19.17,41)),('C13',(0,0,90),(167.68,17)),('C14',(0,0,90),(167.68,126))]),
    dict(name='Lower jaw',slug='Lower_Jaw',parts=[
        ('C02',(0,0,0),(39.4,46.308))]),
    dict(name='Upper head',slug='Upper_Head',parts=[
        ('C01',(180,0,0),(25.602,29.179))]),
    dict(name='Bottom rim and upper teeth',slug='Bottom_Rim_and_Upper_Teeth',parts=[
        ('C09',(0,0,0),(40,40)),
        *[(f'U{i:02}',(0,0,0),(75+24.4*((i-1)%4),80+43*((i-1)//4))) for i in range(1,9)]]),
    dict(name='Top rim and lower teeth',slug='Top_Rim_and_Lower_Teeth',parts=[
        ('B01',(0,0,0),(37,37)),
        *[(f'L{i:02}',(0,0,0),(90+25*((i-1)%3),85+40*((i-1)//3))) for i in range(1,7)]]),
]
NOTES={
'C01':'Retains user-saved broad, shallow orientation; selective support beneath shell and lip.',
'C02':'Retains user-saved broad, shallow orientation; selective support under tray, bowl and sockets.',
'C04':'Rear frame face down; support remaining ledges, keep clip slots and bearings clear.',
'G00':'Mounting pads down; support arms and gear locally. Do not fill the hex hub socket.',
'G02':'Flat gear face down; keep teeth and push-pin holes clear.',
'C12':'Stem foot down; localized supports under upper flange and leaf sockets.',
'C18':'Retains user-saved flipped orientation; selective support, preserve keeper and pin passages.',
'C15':'Bezel face down; PCB cradle above.',
'C13':'Leaf veins up; localized underside supports.',
'C14':'Leaf veins up; localized underside supports.',
'A00':'Mounting feet down; supports under saddle only.',
'A09':'Mounting pad down; local support for thrust keeper.',
'T01':'Flat holes: 0.15 / 0.20 / 0.25 mm per-side clearance. Three dots match the successful user fit.',
'T03':'Test flat tooth roots before the jaws.',
}
for id in [f'A{i:02}' for i in range(1,8)]+['T04','T05']:
    NOTES[id]='PRINT IN PLACE: hinge axes remain vertical. Preserve 22.5-degree partial curl; stop tabs print clear of both limits. No support or brim in joints.'
for id in [f'U{i:02}' for i in range(1,9)]+[f'L{i:02}' for i in range(1,7)]:
    NOTES[id]='Flat 3 mm fang face down; no support. Keep the split root free of paint and brim.'
for id in [f'R{i:02}' for i in range(1,29)]:
    NOTES[id]='3 mm broad face on bed; pin length and split nose lie in the layer plane. PETG; solid infill; no supports in slit.'
for id in ['H01','H02']+[f'F{g}{i}' for g in [1,2] for i in range(1,7)]:
    NOTES[id]='Spline opening up. Trial fit only; fine nozzle/layers for spline detail. No support inside bore.'


def intentional_nesting(p,q,metadata):
    a,c=p['id'],q['id']
    ga,gc=metadata[a].get('print_assembly'),metadata[c].get('print_assembly')
    if ga and ga==gc:return True
    if a in ['C09','B01'] or c in ['C09','B01']:
        other=q if a in ['C09','B01'] else p
        if other['id'].startswith(('U','L')):
            bb=np.array(other['bbox_local_mm'])
            corners=np.array([[x,y] for x in bb[:,0] for y in bb[:,1]])
            assert np.max(np.linalg.norm(corners-[120,120],axis=1))<=65.1
            return True
    return False


def arrays(mesh):
    vv=np.array([[v.X,v.Y,v.Z] for v in mesh.Vertices.ToPoint3dArray()],dtype=np.float64)
    ff=[]
    for a,b,c,d in mesh.Faces:
        ff.append((a,b,c))
        if c!=d: ff.append((a,c,d))
    return vv,np.array(ff,dtype=np.int64)


def tri(mesh):
    return trimesh.Trimesh(*arrays(mesh),process=False)


def bounds(mesh):
    bb=mesh.GetBoundingBox()
    return np.array([[bb.Min.X,bb.Min.Y,bb.Min.Z],[bb.Max.X,bb.Max.Y,bb.Max.Z]])


def translate(mesh,xyz):
    assert mesh.Transform(r.Transform.Translation(*map(float,xyz)))


def orient(mesh,angles,xy):
    for a,axis in zip(angles,[(1,0,0),(0,1,0),(0,0,1)]):
        if a: assert mesh.Transform(r.Transform.Rotation(math.radians(a),r.Vector3d(*axis),r.Point3d(0,0,0)))
    translate(mesh,np.r_[xy,0]-bounds(mesh)[0])


def metrics(mesh):
    m=tri(mesh)
    return dict(
        contact_area_mm2=float(m.area_faces[np.max(m.triangles[:,:,2],axis=1)<.025].sum()),
        down_facing_45deg_area_mm2=float(m.area_faces[(m.face_normals[:,2]<-.7071068)&(m.triangles_center[:,2]>.25)].sum()),
    )


def checked_stl_part(tm):
    """Avoid float32 STL slivers without altering the double-precision CAD mesh."""
    def readback(candidate):
        return trimesh.load_mesh(io.BytesIO(candidate.export(file_type='stl')),file_type='stl',process=True)
    def good(candidate):
        return candidate.is_watertight and candidate.is_winding_consistent and candidate.volume>0 and len(candidate.split(only_watertight=False))==1
    rb=readback(tm)
    if good(rb):return tm,0.0
    # One micron is far below nozzle/layer resolution. Repair only a part whose
    # binary STL round trip otherwise collapses coincident vertices into slivers.
    solid=manifold3d.Manifold(manifold3d.Mesh64(np.array(tm.vertices,dtype=np.float64,copy=True,order='C'),np.array(tm.faces,dtype=np.uint64,copy=True,order='C')))
    assert solid.status()==manifold3d.Error.NoError
    solid=solid.simplify(.001);out=solid.to_mesh64()
    repaired=trimesh.Trimesh(np.asarray(out.vert_properties)[:,:3],np.asarray(out.tri_verts),process=False)
    assert good(readback(repaired))
    assert math.isclose(repaired.volume,tm.volume,rel_tol=2e-5)
    assert np.max(np.abs(repaired.bounds-tm.bounds))<.0011
    return repaired,.001


def view(doc,name,center,halfwidth,halfheight,default=False):
    v=r.ViewInfo();v.Name=name
    v.Viewport.SetCameraLocation(r.Point3d(center[0],center[1],1600))
    v.Viewport.SetCameraDirection(r.Vector3d(0,0,-1))
    v.Viewport.SetCameraUp(r.Vector3d(0,1,0))
    v.Viewport.TargetPoint=r.Point3d(center[0],center[1],0)
    v.Viewport.ChangeToParallelProjection(True)
    v.Viewport.SetFrustum(-halfwidth,halfwidth,-halfheight,halfheight,1,2600)
    doc.NamedViews.Add(v)
    if default:doc.Views.Add(v)


def main():
    metadata={p['id']:p for p in json.loads((ROOT/'validation/parts.json').read_text())}
    # Reconstruct each captive print assembly from its common print frame.
    for group,origin,ys in [('PIP_TONGUE',(15,15),{f'A{i:02}':0 for i in range(1,8)}),('PIP_TEST',(100,175),{'T04':0,'T05':0})]:
        mins={id:np.array(metadata[id]['print_bbox_min_mm']) for id in ys}
        base=np.min(list(mins.values()),axis=0)
        for bed in BEDS:
            bed['parts']=[(id,rot,tuple(np.array(origin)+(mins[id]-base)[:2])) if id in mins else (id,rot,xy) for id,rot,xy in bed['parts']]
    original=r.File3dm.Read(str(MODEL)); assert original
    source={}
    for obj in original.Objects:
        if original.Layers[obj.Attributes.LayerIndex].Name.startswith('PRINT '):
            id=obj.Attributes.GetUserString('Part ID')
            assert id not in source
            source[id]=obj
    ids=[x[0] for bed in BEDS for x in bed['parts']]
    assert len(ids)==len(set(ids))==len(metadata) and set(ids)==set(source)==set(metadata)
    doc=r.File3dm();doc.Settings.ModelUnitSystem=r.UnitSystem.Millimeters;doc.Settings.ModelAbsoluteTolerance=.01
    doc.Strings['Project']='Piranha Clock V6 / eight 240 x 240 mm print beds'
    doc.Strings['Export']='Select a numbered BED layer or its group; guides are locked. Ready-made STL files in print_beds use local plate coordinates.'
    doc.Strings['Print warning']='Supports and brim must be generated and checked in your slicer.  Not physically printed.'
    doc.Strings['Source SHA256']=hashlib.sha256(MODEL.read_bytes()).hexdigest()
    mats={}
    for mi,mat in enumerate(original.Materials):
        mats[mi]=doc.Materials.Add(mat)
    layer_colors=[(174,102,112,255),(100,143,127,255),(114,139,76,255),(175,133,111,255),(164,86,92,255),(58,128,94,255),(205,187,137,255)]
    for i,bed in enumerate(BEDS,1):
        ly=r.Layer();ly.Name=f'BED {i:02} - {bed["name"]}';ly.Color=layer_colors[(i-1)%len(layer_colors)];ly.Visible=True
        bed['layer_index']=doc.Layers.Add(ly)
        g=r.Group();g.Name=f'BED_{i:02}_PRINT';doc.Groups.Add(g)
        bed['group_index']=doc.Groups.FindName(g.Name).Index
    ly=r.Layer();ly.Name='00 GUIDES - locked - DO NOT EXPORT';ly.Color=(125,145,139,255);ly.Locked=True
    guides=doc.Layers.Add(ly)
    guideattrs=r.ObjectAttributes();guideattrs.LayerIndex=guides
    (ROOT/'print_beds').mkdir(exist_ok=True)
    report=[];rows=[];render_data=[]
    for i,bed in enumerate(BEDS,1):
        offset=np.array([((i-1)%4)*300,(1-(i-1)//4)*300,0])
        layer=doc.Layers[bed['layer_index']]
        layer.SetUserString('Bed size mm','240 x 240')
        layer.SetUserString('Bed origin XYZ mm',','.join(map(str,offset)))
        stl_name=f'Bed_{i:02}_{bed["slug"]}.stl'
        layer.SetUserString('Ready STL','print_beds/'+stl_name)
        part_report=[];stl_meshes=[];rmesh=[];solid_parts={}
        for id,angles,xy in bed['parts']:
            src=source[id];m=src.Geometry.Duplicate();assert isinstance(m,r.Mesh)
            translate(m,-bounds(m)[0]);before=metrics(m);original_tri=tri(m)
            orient(m,angles,xy)
            bb=bounds(m);tm=tri(m);after=metrics(m)
            assert m.IsValid and m.IsClosed and tm.is_watertight and tm.is_winding_consistent and tm.volume>0,id
            assert len(tm.faces)==len(original_tri.faces)
            assert math.isclose(tm.volume,original_tri.volume,rel_tol=1e-9)
            assert bb[0,0]>=EDGE-1e-5 and bb[0,1]>=EDGE-1e-5 and bb[1,0]<=240-EDGE+1e-5 and bb[1,1]<=240-EDGE+1e-5,(id,bb)
            assert abs(bb[0,2])<1e-6
            stl_part,cleanup_tolerance=checked_stl_part(tm)
            stl_meshes.append(stl_part);rmesh.append((id,m.Duplicate()))
            solid_parts[id]=manifold3d.Manifold(manifold3d.Mesh64(np.array(tm.vertices,np.float64,copy=True),np.array(tm.faces,np.uint64,copy=True)))
            a=r.ObjectAttributes();a.Name=f'{id} | {metadata[id]["name"]}';a.LayerIndex=bed['layer_index']
            a.ObjectColor=src.Attributes.ObjectColor;a.ColorSource=r.ObjectColorSource.ColorFromObject
            a.MaterialSource=r.ObjectMaterialSource.MaterialFromObject;a.MaterialIndex=mats[src.Attributes.MaterialIndex]
            a.AddToGroup(bed['group_index'])
            for key,value in [('Part ID',id),('Print bed',f'{i:02}'),('Support guidance',NOTES.get(id,'Flat original base down; inspect small features in slicer.')),('Original part STL',metadata[id]['stl']),('Bed STL','print_beds/'+stl_name),('Bed origin XYZ mm',','.join(map(str,offset)))]:a.SetUserString(key,value)
            translate(m,offset);assert m.IsClosed and m.IsValid;doc.Objects.AddMesh(m,a)
            p=dict(id=id,name=metadata[id]['name'],bbox_local_mm=bb.tolist(),size_mm=(bb[1]-bb[0]).tolist(),rotation_from_individual_stl_deg=list(angles),triangles=len(tm.faces),volume_mm3=float(tm.volume),vertex_colors=len(m.VertexColors),orientation_note=NOTES.get(id,'Flat original base down.'),orientation_metrics_before=before,orientation_metrics_after=after,stl_cleanup_tolerance_mm=cleanup_tolerance,stl_triangles=len(stl_part.faces),stl_volume_change_fraction=float(stl_part.volume/tm.volume-1))
            part_report.append(p)
            rows.append([i,id,p['name'],*np.round(p['size_mm'],3),*angles,*np.round(bb[0,:2],3),p['orientation_note']])
        gaps=[]
        for j,p in enumerate(part_report):
            for q in part_report[j+1:]:
                aa=np.array(p['bbox_local_mm']);ab=np.array(q['bbox_local_mm'])
                sep=np.maximum(0,np.maximum(aa[0,:2]-ab[1,:2],ab[0,:2]-aa[1,:2]))
                dist=float(np.linalg.norm(sep));
                if intentional_nesting(p,q,metadata):continue
                if dist<GAP-1e-5:
                    # Preserve valid user nesting inside open frames; bounding
                    # rectangles overlap although the actual solids are apart.
                    dist=solid_parts[p['id']].min_gap(solid_parts[q['id']],GAP)
                assert dist>=GAP-1e-5,(p['id'],q['id'],dist)
                gaps.append(dist)
        combined=trimesh.util.concatenate(stl_meshes);combined.export(ROOT/'print_beds'/stl_name)
        # Reopen the actual STL: float32 output can change coordinates slightly.
        check=trimesh.load_mesh(ROOT/'print_beds'/stl_name,process=True)
        components=check.split(only_watertight=False)
        assert len(components)==len(part_report),(i,len(components),len(part_report))
        assert all(c.is_watertight and c.is_winding_consistent and c.volume>0 for c in components)
        assert math.isclose(check.volume,combined.volume,rel_tol=5e-6)
        corners=[(0,0),(240,0),(240,240),(0,240),(0,0)]
        for inset in [0,10]:
            pts=[r.Point3d(offset[0]+(inset if x==0 else 240-inset),offset[1]+(inset if y==0 else 240-inset),-.15) for x,y in corners]
            doc.Objects.AddCurve(r.PolylineCurve(pts),guideattrs)
        doc.Objects.AddTextDot(f'BED {i:02} | {bed["name"]}\n240 x 240 mm | {len(part_report)} parts',r.Point3d(offset[0]+120,offset[1]-17,0),guideattrs)
        view(doc,f'BED {i:02} - {bed["name"]}',offset[:2]+120,134,134)
        bed_result=dict(bed=i,name=bed['name'],layer=layer.Name,bed_size_mm=[240,240],rhino_origin_mm=offset.tolist(),stl='print_beds/'+stl_name,stl_origin_mm=[0,0,0],part_count=len(part_report),max_height_mm=float(check.bounds[1,2]),min_pair_bbox_gap_mm=min(gaps) if gaps else None,parts=part_report,stl_watertight_components=len(components),stl_sha256=hashlib.sha256((ROOT/'print_beds'/stl_name).read_bytes()).hexdigest())
        report.append(bed_result);render_data.append((bed_result,rmesh))
        print(f'BED {i:02}: {len(part_report)} closed parts, max Z {check.bounds[1,2]:.2f} mm',flush=True)
    view(doc,'ALL PRINT BEDS - top',(570,265),615,320,True)
    assert doc.Write(str(OUTPUT),7)
    rd=r.File3dm.Read(str(OUTPUT));rm=[o for o in rd.Objects if isinstance(o.Geometry,r.Mesh)]
    assert len(rm)==len(metadata) and all(o.Geometry.IsValid and o.Geometry.IsClosed for o in rm)
    assert {o.Attributes.GetUserString('Part ID') for o in rm}==set(ids)
    assert len([ly for ly in rd.Layers if ly.Name.startswith('BED ')])==len(BEDS)
    assert all(rd.Layers[o.Attributes.LayerIndex].Name.startswith('BED ') for o in rm)
    assert all(isinstance(o.Geometry,r.Mesh) for o in rd.Objects if rd.Layers[o.Attributes.LayerIndex].Name.startswith('BED '))
    assert rd.Settings.ModelUnitSystem==r.UnitSystem.Millimeters
    result=dict(model=OUTPUT.relative_to(ROOT).as_posix(),source_model=MODEL.relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest(),bed_count=len(BEDS),unique_part_count=len(metadata),closed_rhino_meshes=len(rm),all_parts_included_once=True,edge_margin_mm=EDGE,minimum_unrelated_solid_gap_mm=GAP,max_height_mm=max(b['max_height_mm'] for b in report),geometry_change='Rhino: rigid transforms only, identical face counts and volumes. STL: selective 0.001 mm sliver cleanup where float32 export needs it.',supports_generated=False,sliced=False,physical_print_tested=False,metric_note='Bounding-box gaps used where separated; exact solid distances checked for nested open frames. Tongue captive clearances checked separately. Down-facing area is not support-volume simulation.',beds=report)
    (ROOT/'validation/print_beds.json').write_text(json.dumps(result,indent=2)+'\n')
    with (ROOT/'docs/print_beds.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['Bed','ID','Part','X mm','Y mm','Z mm','Extra rotation X deg','Extra rotation Y deg','Extra rotation Z deg','Bed local min X mm','Bed local min Y mm','Orientation and supports']);w.writerows(rows)
    quick_fit_bed()
    render(render_data)
    print('Saved and reopened: eight bed layers; all closed meshes; no hardware or duplicate assembly parts.',flush=True)


def quick_fit_bed():
    """Refresh the user's optional small Bed 00 test export without duplicates
    in the eight full-production Rhino layers."""
    specs=[('T01.stl',(10,10),0),('T03.stl',(75,10),0),
           ('T02.stl',(15,43),90),('R15.stl',(15,60),90),
           ('R16.stl',(15,75),90),('R17.stl',(15,90),90),
           ('Hinge_Sample_Print_in_Place.stl',(100,45),0)]
    meshes=[]
    for filename,xy,angle in specs:
        mesh=trimesh.load_mesh(ROOT/'stl'/filename,process=True)
        if angle:mesh.apply_transform(trimesh.transformations.rotation_matrix(math.radians(angle),[0,0,1]))
        mesh.apply_translation(np.r_[xy,0]-mesh.bounds[0]);meshes.append(mesh)
    output=ROOT/'print_beds/Bed_00_Fit_Samples.stl'
    trimesh.util.concatenate(meshes).export(output)
    read=trimesh.load_mesh(output,process=True);parts=read.split(only_watertight=False)
    assert len(parts)==8 and all(m.is_watertight and m.volume>0 for m in parts)
    assert np.all(read.bounds[0]>=-1e-6) and np.all(read.bounds[1,:2]<230)
    (ROOT/'validation/quick_fit_bed.json').write_text(json.dumps(dict(file='print_beds/'+output.name,optional_subset=True,parts=['T01','T02','T03','T04','T05','R15','R16','R17'],closed_components=8,note='Updated user quick-fit export. All parts also occur on full Bed 01; do not print twice unless spares are wanted.',physical_printed=False),indent=2),encoding='utf-8')

def render(data):
    import pyvista as pv
    from PIL import Image,ImageDraw,ImageFont
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',21)
    small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
    large=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',35)
    for mode in ['overview','isometric']:
        canvas=Image.new('RGB',(2400,1410),'#f2f0e9');draw=ImageDraw.Draw(canvas)
        draw.text((35,20),'PIRANHA CLOCK / EIGHT PRINT BEDS',font=large,fill='#213a33')
        draw.text((37,69),'240 x 240 mm each  |  Captive tongue, flat teeth, push pins and spline fit samples  |  all dimensions in mm',font=font,fill='#50655b')
        for n,(bed,meshes) in enumerate(data):
            plot=pv.Plotter(off_screen=True,window_size=(570,510));plot.set_background('#f2f0e9')
            plot.add_mesh(pv.Plane(center=(120,120,-.35),i_size=240,j_size=240),color='#e3e4dc',lighting=False)
            for coords,col,width in [(np.array([[0,0,0],[240,0,0],[240,240,0],[0,240,0],[0,0,0]]),'#71897e',2),(np.array([[10,10,0],[230,10,0],[230,230,0],[10,230,0],[10,10,0]]),'#b4beb3',1)]:
                plot.add_lines(coords,color=col,width=width,connected=True)
            for id,m in meshes:
                vv,ff=arrays(m);poly=pv.PolyData(vv,np.column_stack((np.full(len(ff),3),ff)).ravel())
                if len(m.VertexColors)==len(vv):
                    poly['rgb']=np.array(list(m.VertexColors),dtype=np.uint8)[:,:3]
                    plot.add_mesh(poly,scalars='rgb',rgb=True,show_scalar_bar=False,smooth_shading=True,ambient=.4,specular=.1)
                else:plot.add_mesh(poly,color='#ad7770',smooth_shading=True)
                bb=bounds(m)
                if mode=='overview':
                    pos=((bb[0,0]+bb[1,0])/2,bb[0,1]+(bb[1,1]-bb[0,1])/2,bb[1,2]+2)
                    plot.add_point_labels([pos],[id],font_size=15,bold=True,show_points=False,always_visible=True,text_color='#152c25',shape_color='#fffdf4',shape_opacity=.9,margin=3)
            if mode=='overview':
                plot.camera_position=[(120,120,900),(120,120,0),(0,1,0)];plot.camera.parallel_scale=133
            else:
                plot.camera_position=[(430,-480,480),(120,120,50),(0,0,1)];plot.camera.parallel_scale=175
                if bed['bed']==5:
                    plot.camera_position=[(430,720,480),(120,120,50),(0,0,1)]
            plot.camera.parallel_projection=True;plot.enable_anti_aliasing('ssaa')
            img=Image.fromarray(plot.screenshot(return_img=True));plot.close()
            x=(n%4)*600+15;y=(n//4)*625+112
            canvas.paste(img,(x,y));draw.text((x+10,y+514),f'{bed["bed"]:02}  {bed["name"]}',font=font,fill='#213a33')
            count_label='part' if bed['part_count']==1 else 'parts'
            draw.text((x+10,y+545),f'{bed["part_count"]} {count_label}  /  tallest {bed["max_height_mm"]:.1f} mm',font=small,fill='#50655b')
        draw.text((37,1370),'Supports and brims are added in the slicer. Bed outlines and labels are guides only; they are not in the STLs.',font=small,fill='#50655b')
        canvas.save(ROOT/'images'/f'print_beds_{mode}.png')


if __name__=='__main__':main()
