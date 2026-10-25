"""Record engagement margins and draw a section through the actual gear meshes."""
import json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Arc
import build_segmented as v
v.load()
lower=v.PARTS['G02']['s'];pinion=v.PARTS['G00']['s']
rp,rg,alpha=8.,32.,math.radians(25)
contact_ratio=(math.sqrt(9**2-(rp*math.cos(alpha))**2)+math.sqrt(33**2-(rg*math.cos(alpha))**2)-40*math.sin(alpha))/(math.pi*math.cos(alpha))
report=dict(module_mm=1,pressure_angle_deg=25,center_distance_mm=40,pinion_teeth=16,large_pitch_circle_teeth=64,retained_sector_teeth=16,sector_deg=[45,135],contact_line_in_sector_coordinates_deg=[90,102.5],minimum_line_to_cut_edge_deg=32.5,ideal_standard_transverse_contact_ratio=contact_ratio,ratio=4,gear_inward_shift_mm=21.4,sector_volume_cm3=lower.volume()/1000,physical_tested=False)
old=v.ROOT.parent/'v3-geared-mouth'/'validation'/'parts.json'
if old.exists():
    previous=next(p for p in json.loads(old.read_text()) if p['id']=='G02')
    report.update(previous_gear_volume_cm3=previous['volume_cm3'],volume_reduction_percent=100*(1-lower.volume()/1000/previous['volume_cm3']))
(v.ROOT/'validation'/'sector.json').write_text(json.dumps(report,indent=2))
fig,axs=plt.subplots(1,2,figsize=(11,6),facecolor='#111e1a')
for ax,q,title in zip(axs,[0,50],['RESTING','OPEN: upper +50° / lower −12.5°']):
    ax.set_facecolor('#111e1a')
    for id,pivot,upper in [('G00',v.U,True),('G02',v.L,False)]:
        s=v.jaw_pose(v.PARTS[id]['s'],q,upper)
        vv,ff=v.meshdata(s);tm=v.trimesh.Trimesh(vv,ff,process=False)
        sec=tm.section(plane_origin=[-42,0,0],plane_normal=[1,0,0])
        for curve in sec.discrete:
            ax.plot(curve[:,1]+50,curve[:,2]+32,color='#dcb76d',linewidth=1.2)
    ax.add_patch(Circle((0,0),32,fill=False,color='#6c8274',linestyle='--',linewidth=1))
    ax.plot([0,0],[0,40],color='#acbdac',linestyle=':',linewidth=1)
    ax.scatter([0,0],[0,40],s=14,c='#e9e4d4')
    ax.annotate('32 mm pitch radius',xy=(30,0),xytext=(6,-23),color='#b7c3b9',fontsize=9,arrowprops=dict(arrowstyle='-',color='#7b9383'))
    ax.text(12,40,'16-tooth\npinion',color='#e9e4d4',fontsize=10,va='center')
    ax.text(-42,12,'Retained\nquadrant',color='#e9e4d4',fontsize=10)
    ax.set_title(title,color='#e9e4d4',fontsize=12,pad=14)
    ax.set_xlim(-45,45);ax.set_ylim(-34,53);ax.set_aspect('equal');ax.axis('off')
fig.suptitle('Same 4:1 ratio — only the unused teeth are removed',color='#e9e4d4',fontsize=16,y=.97)
fig.text(.5,.025,'Actual CAD cross-sections. Dashed circle: original 64-tooth pitch circle. Full hub retained for mounting.',ha='center',color='#b7c3b9',fontsize=10)
fig.tight_layout(rect=[0,.055,1,.94]);fig.savefig(v.ROOT/'images'/'sector_gear_detail.png',dpi=160,facecolor=fig.get_facecolor());plt.close(fig)
print(json.dumps(report,indent=2))
