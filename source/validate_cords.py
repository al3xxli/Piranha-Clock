"""Clearance of simplified cord tubes; not rope contact simulation."""
import json
import build_segmented as v
from validate_motion import overlap
v.load();issues={}
for curl in [45,35,25,15,0]:
    for name,cord,col in v.cords(curl,50):
        for id,p in v.PARTS.items():
            if p['group'] in ['test','fixed']:continue
            volume=overlap(cord,v.posed(p,50,curl))
            if volume>.02:issues.setdefault(name+':'+id,[]).append([curl,round(volume,4)])
report=dict(poses=5,threshold_mm3=.02,issues=issues,scope='Simplified free-string and elastic tubes against printed head parts; excludes knots, two-strand contact, wound string, friction and elastic force.')
(v.ROOT/'validation'/'cords.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert not issues, 'Cord interference needs relief or a revised path'
