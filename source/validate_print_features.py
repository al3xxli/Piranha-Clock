"""Inspect actual solids and exported captive assemblies; no print/strength claims."""
import json,itertools
import numpy as np
import trimesh
import build_segmented as v
from validate_motion import overlap

def main():
    v.load();P=v.PARTS;b=v.b
    problems=[];hinges=[]
    for c in np.linspace(0,45,91):
        for i in range(1,7):
            a=P[f'A{i:02}']['s'];d=P[f'A{i+1:02}']['s'].rotate((float(c),0,0)).translate((0,22,0))
            vol=overlap(a,d)
            if vol>.01:problems.append(dict(joint=i,angle_deg=float(c),overlap_mm3=vol))
    # Retention check: translating the female knuckle 1 mm either way is blocked.
    for i in range(1,7):
        a=P[f'A{i:02}']['s'];d=P[f'A{i+1:02}']['s'].translate((0,22,0))
        hits=[overlap(a,d.translate((dx,0,0))) for dx in [-1,1]]
        assert min(hits)>.01,(i,hits)
        hinges.append(dict(joint=i,axial_displacement_test_mm=[-1,1],retaining_intersection_mm3=hits))
    composites=[]
    for file,count in [('Tongue_Print_in_Place.stl',7),('Hinge_Sample_Print_in_Place.stl',2)]:
        tm=trimesh.load_mesh(v.ROOT/'stl'/file,process=True);pieces=tm.split(only_watertight=False)
        assert len(pieces)==count and all(p.is_watertight and p.volume>0 for p in pieces)
        assert max(abs(p.bounds[0,2]) for p in pieces)<1e-5
        parts=[b.M(b.m.Mesh64(np.array(p.vertices,np.float64,copy=True),np.array(p.faces,np.uint64,copy=True))) for p in pieces]
        assert max([overlap(a,c) for a,c in itertools.combinations(parts,2)]+[0])<.01
        composites.append(dict(file=file,captive_closed_components=count,all_components_start_on_bed=True,size_mm=(tm.bounds[1]-tm.bounds[0]).tolist()))
    teeth=[];bad_crowns=[]
    for row in json.loads((v.ROOT/'validation/tooth_sockets.json').read_text()):
        p=P[row['id']];s=v.print_solid(p);bb=s.bounding_box()
        assert abs(bb[5]-bb[2]-3)<1e-5
        # Exposed crown must insert without hitting jaw. Flexing root barbs are
        # deliberately excluded; they compress through the entry and recover.
        z=row['origin'][2]
        crown=p['s']^b.box(-150,-150,z-80 if row['upper'] else z,300,300,80)
        for d in np.linspace(0,20,41):
            shift=-float(d) if row['upper'] else float(d)
            vol=overlap(crown.translate((0,0,shift)),P[row['jaw']]['s'])
            if vol>.01:bad_crowns.append(dict(id=row['id'],withdrawal_mm=float(d),overlap_mm3=vol))
        teeth.append(dict(id=row['id'],flat_print_thickness_mm=bb[5]-bb[2],installed_jaw_overlap_mm3=overlap(p['s'],P[row['jaw']]['s'])))
    # All assembly parts, with only narrowly defined intended press ribs removed.
    ss={id:v.posed(p,0,45) for id,p in P.items() if p['group']!='test'}
    assembly=[];allowed=[]
    for a,c in itertools.combinations(ss,2):
        vol=overlap(ss[a],ss[c])
        if vol<=.05:continue
        pair=set([a,c]);mask=b.M()
        if pair=={'A00','A01'}:
            mask=b.box(-8.351,-4.001,-1.701,.052,7.002,3.402)+b.box(8.299,-4.001,-1.701,.052,7.002,3.402)
            mask=mask.transform(v.section_matrix(0,0)).translate((0,0,b.Z))
        for leaf,x,y,z in [('C13',-27,-40,162),('C14',19,-48,184)]:
            if pair=={'C12',leaf}:
                mask=b.box(x-.001,y-3.381,z-1.401,7.002,.082,2.802)+b.box(x-.001,y+3.299,z-1.401,7.002,.082,2.802)
        remainder=max(0.,((ss[a]^ss[c])-mask).volume())
        (assembly if remainder>.05 else allowed).append(dict(pair=[a,c],total_intersection_mm3=vol,outside_press_ribs_mm3=remainder))
    result=dict(hinge_motion_samples=546,hinge_intersections=problems,hinge_axial_capture=hinges,print_in_place_exports=composites,flat_teeth=teeth,crown_insertion_samples=574,crown_insertion_issues=bad_crowns,unintended_assembly_intersections=assembly,intentional_press_rib_contacts=allowed,physical_printed=False,slicer_checked=False,force_or_fatigue_simulated=False)
    (v.ROOT/'validation/print_features.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:val for k,val in result.items() if k not in ['flat_teeth','hinge_axial_capture']},indent=2),flush=True)
    assert not problems and not bad_crowns and not assembly

if __name__=='__main__':main()
