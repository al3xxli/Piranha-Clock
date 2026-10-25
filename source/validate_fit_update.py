"""Check actual flat print faces and nonzero captive-stop export clearance."""
import json
import numpy as np
import trimesh
import build_segmented as v

def main():
    v.load();pins=[]
    for id,p in v.PARTS.items():
        if 'flat_pin_axis' not in p:continue
        s=v.print_solid(p);bb=np.array(s.bounding_box());s=s.translate(-bb[:3])
        vv,ff=v.meshdata(s);tm=trimesh.Trimesh(vv,ff,process=False)
        contact=float(tm.area_faces[np.max(tm.triangles[:,:,2],axis=1)<1e-5].sum())
        assert abs((bb[5]-bb[2])-3)<1e-6 and contact>15,(id,bb,contact)
        pins.append(dict(id=id,print_thickness_mm=3,continuous_flat_contact_area_mm2=contact))
    assert len(pins)==29
    shank=v.PARTS['T02']['s']^v.b.box(-4,-4,1,8,8,6)
    fit_gap=shank.translate((45,9,0)).min_gap(v.PARTS['T01']['s'],.5)
    assert fit_gap>=.24,fit_gap
    hinges=[]
    for i in range(1,7):
        a=v.PARTS[f'A{i:02}']['s']
        b=v.PARTS[f'A{i+1:02}']['s'].rotate((v.PRINT_CURL,0,0)).translate((0,22,0))
        stop=a^v.b.box(-12.61,20.8,-6.01,3.61,2.4,3.65)
        tab_gap=stop.min_gap(b,1.5);all_gap=a.min_gap(b,1)
        assert tab_gap>=.79 and all_gap>=.34,(i,tab_gap,all_gap)
        hinges.append(dict(joint=i,print_angle_deg=v.PRINT_CURL,moving_tab_gap_mm=tab_gap,minimum_pair_gap_mm=all_gap))
    out=trimesh.load_mesh(v.ROOT/'stl/Tongue_Print_in_Place.stl',process=True)
    pieces=out.split(only_watertight=False)
    solids=[v.b.M(v.b.m.Mesh64(np.array(p.vertices,np.float64,copy=True),np.array(p.faces,np.uint64,copy=True))) for p in pieces]
    min_export_gap=min(a.min_gap(b,1) for j,a in enumerate(solids) for b in solids[j+1:])
    assert len(pieces)==7 and min_export_gap>.34
    assert all(abs(p.bounds[0,2])<1e-5 for p in pieces)
    result=dict(user_feedback='Prior three-dot round pin hole fits; prior tongue printed but the moving stop tab welded to the outer hinge and required snipping.',flat_pin_count=len(pins),pins=pins,production_clearance_per_side_mm=.25,production_main_profile_mm=[4,3],production_main_keyed_hole_mm=[4.5,3.5],three_dot_coupon_shank_gap_mm=fit_gap,jaw_running_bearing='Round 4.5 mm bore around flat-sided 4 mm axle; fixed frame keyed.',tongue_print_orientation='Previous side-standing orientation, hinge axes vertical; joints at 22.5 degrees between end stops.',tongue_hinges=hinges,export_minimum_component_gap_mm=min_export_gap,whole_tongue_printed_together=True,each_section_has_bed_contact=True,new_geometry_physically_printed=False,mechanical_strength_tested=False)
    (v.ROOT/'validation/fit_update.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:val for k,val in result.items() if k not in ['pins','tongue_hinges']},indent=2))

if __name__=='__main__':main()
