"""Render real CAD meshes, with explicit idealised cord paths."""
import math,sys
import numpy as np
import pyvista as pv
from PIL import Image,ImageDraw,ImageFont
import build_segmented as v
v.load();b=v.b
COLORS={id:b.color_vertices(b.meshdata(p['s'])[0],p) for id,p in v.PARTS.items()}

def render(q=50,curl=0,mode='full',size=(1100,1200)):
    plot=pv.Plotter(off_screen=True,window_size=size,lighting='none');plot.set_background('#111e1a')
    def mesh(s,color,p=None,opacity=1):
        vv,ff=b.meshdata(s);m=pv.PolyData(vv,np.column_stack([np.full(len(ff),3),ff]).ravel().astype(np.int64))
        if p:
            m['rgb']=COLORS[p['id']]
            plot.add_mesh(m,scalars='rgb',rgb=True,smooth_shading=True,split_sharp_edges=True,specular=.22,ambient=.2,show_scalar_bar=False,opacity=opacity)
        else:plot.add_mesh(m,color=np.array(b.COLORS[color])/255,smooth_shading=True,specular=.2,ambient=.22,opacity=opacity)
    for p in v.PARTS.values():
        if p['group']=='test':continue
        if mode!='full' and p['group']=='fixed' and p['id'] not in ['R15','R16','R17']:continue
        if mode=='mechanism' and (p['id'].startswith('U') or p['id'] in ['C01','C18','C09','C10','C11','C12','C13','C14','C15','C16','C17']):continue
        if mode=='head' and p['id'] in ['C09','C10','C11','C12','C13','C14','C15','C16','C17']:continue
        if mode=='tongue' and not p['id'].startswith('A'):continue
        mesh(v.posed(p,q,curl),p['color'],p)
    for nm,s,c in v.hardware(q,curl):
        if mode=='tongue' and not ('pin' in nm):continue
        if mode!='full' and any(k in nm for k in ['UNO','DS3231','TM1637','USER CUT']):continue
        mesh(s,c)
    for nm,s,c in v.cords(curl,q):mesh(s,c)
    for pos,power,col in [((240,300,520),1.2,'#fff1dc'),((-280,100,300),.75,'#b9d6ed'),((10,-300,460),1.0,'#f9b69e')]:plot.add_light(pv.Light(position=pos,focal_point=(0,0,230),intensity=power,color=col,positional=False))
    if mode=='full':
        plot.add_mesh(pv.Plane(center=(0,0,0),direction=(0,0,1),i_size=2000,j_size=2000),color='#17231f')
        plot.add_mesh(pv.Text3D('12:00',depth=.1,height=13,center=(0,72,52),normal=(0,1,0)),color='#c5dca4',lighting=False)
        plot.camera_position=[(390,700,405),(0,24,205),(0,0,1)];plot.camera.parallel_scale=235
    elif mode=='mechanism':plot.camera_position=[(-330,270,355),(-5,5,285),(0,0,1)];plot.camera.parallel_scale=140
    elif mode=='head':plot.camera_position=[(-330,270,355),(0,25,295),(0,0,1)];plot.camera.parallel_scale=165
    else:plot.camera_position=[(300,140,350),(10,45,245),(0,0,1)];plot.camera.parallel_scale=120
    plot.camera.parallel_projection=True;plot.enable_anti_aliasing('ssaa')
    try:plot.enable_ssao(radius=10,bias=.5,kernel_size=32)
    except Exception:pass
    img=plot.screenshot(return_img=True);plot.close();return Image.fromarray(img)

def stills():
    for name,q,curl,mode in [('assembled_extended.png',50,0,'full'),('assembled_curled.png',0,45,'full'),('mechanism_curled.png',50,45,'mechanism'),('tongue_detail.png',50,18,'tongue'),('left_cheek_open.png',50,0,'head'),('left_cheek_closed.png',0,45,'head')]:
        render(q,curl,mode).save(v.ROOT/'images'/name);print(name,flush=True)

def animate():
    frames=[];durations=[]
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',21);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
    states=[]
    for t in np.linspace(0,1,7):states.append((50*(3*t*t-2*t*t*t),45,'1  MG995 opens BOTH jaws through 4:1 gears',130))
    for t in np.linspace(0,1,13):states.append((50,v.curl_for_fraction(3*t*t-2*t*t*t),'2  MG90S winds the tendon; tongue unrolls',75))
    states.append((50,0,'3  Cuckoo!',650))
    for t in np.linspace(0,1,13):states.append((50,v.curl_for_fraction(1-3*t*t+2*t*t*t),'4  Drum unwinds; elastic links curl the tongue',85))
    for t in np.linspace(0,1,7):states.append((50*(1-3*t*t+2*t*t*t),45,'5  Both jaws close after the tongue curls',130))
    states.append((0,45,'Ready for the next hour',900))
    for n,(q,curl,label,dur) in enumerate(states):
        frame=Image.new('RGB',(1240,680),'#111e1a');frame.paste(render(q,curl,'full',(520,560)),(0,62));frame.paste(render(q,curl,'mechanism',(720,560)),(520,62))
        draw=ImageDraw.Draw(frame);draw.text((26,17),label,font=font,fill='#e9e2cf');draw.text((550,53),'SKULL + CHEEK REMOVED  |  gold: pull string  /  ivory: elastic',font=small,fill='#cec5a9')
        draw.text((24,635),'V6 actual geometry / captive hinges and custom hubs. Idealized motion; fit and elastic return need bench testing.',font=small,fill='#bcc8bd')
        frames.append(frame);durations.append(dur);print('frame',n+1,'/',len(states),flush=True)
    frames[0].save(v.ROOT/'images'/'internal_gears_mechanism.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=2,optimize=False)

if __name__=='__main__':
    if '--gif' in sys.argv:animate()
    else:stills()


