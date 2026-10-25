"""Sample rigid solids, including the true involute tooth meshes."""
import json,itertools,sys
import numpy as np
import build_segmented as v

def overlap(a,b):
    aa=np.array(a.bounding_box());bb=np.array(b.bounding_box())
    if np.any(aa[:3]>=bb[3:]) or np.any(bb[:3]>=aa[3:]):return 0.
    return max(0.,(a^b).volume())

def run(quick=False):
    v.load();issues={}
    selected={id:p for id,p in v.PARTS.items() if p['group']!='test' and (p['group']!='fixed' or id=='C12')}
    states=[(q,45) for q in np.linspace(0,50,6 if quick else 101)]+[(50,c) for c in np.linspace(45,0,6 if quick else 91)]
    for i,(q,c) in enumerate(states):
        ss={id:v.posed(p,q,c) for id,p in selected.items()}
        for a,b in itertools.combinations(ss,2):
            vol=overlap(ss[a],ss[b]);key=a+':'+b
            if set([a,b])==set(['A00','A01']) and vol>.05:
                mask=v.b.box(-8.351,-4.001,-1.701,.052,7.002,3.402)+v.b.box(8.299,-4.001,-1.701,.052,7.002,3.402)
                mask=v.jaw_pose(mask.transform(v.section_matrix(0,0)),q).translate((0,0,v.b.Z))
                vol=max(0.,((ss[a]^ss[b])-mask).volume())
            if vol>.05 and vol>issues.get(key,{}).get('overlap_mm3',0):issues[key]=dict(overlap_mm3=round(vol,4),upper_deg=q,lower_deg=-q/4,curl_deg=c)
        for name,hw,col in v.hardware(q,c):
            if not (('MG' in name and 'case' in name) or name.startswith('Envelope')):continue
            for id,s in ss.items():
                vol=overlap(s,hw);key=id+':'+name
                if vol>.05 and vol>issues.get(key,{}).get('overlap_mm3',0):issues[key]=dict(overlap_mm3=round(vol,4),upper_deg=q,lower_deg=-q/4,curl_deg=c)
        if i%20==0:print('pose',i+1,'/',len(states),'issue pairs',len(issues),flush=True)
    result=dict(poses=len(states),issues=issues,threshold_mm3=.05,physical_tested=False,intentional_compression='Only the two 0.05 mm tongue-root press ribs are excluded by explicit spatial masks.',scope='All rigid head parts, custom hubs, push pins, captive tongue hinges, stem and servo case envelopes. Equal-angle kinematics; no spring, friction or flexure simulation.')
    (v.ROOT/'validation'/('quick.json' if quick else 'motion.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':run('--quick' in sys.argv)
