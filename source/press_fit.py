"""V6: removable push pins, captive tongue joints, flat teeth and sleeve rims.

Nominal prototype fits for PETG and a 0.4 mm nozzle. Coupons are mandatory
before large prints; no force, fatigue or servo-horn fit is inferred from CAD.
"""
import json, math
import numpy as np
import base_geometry as b
import build_segmented as v
import mouth_geometry as mouth
from base_geometry import box,cyl,cx,cy,sphere,tube,union,beamx,add
P=b.PARTS
JOINTS=[]
PIN_CLEARANCE=.25  # User's successful three-dot 4.5 mm hole / 4 mm pin.
PIN_THICKNESS=3.0

def setpart(id,s,name=None):
    P[id]['s']=s
    if name:P[id]['name']=name

def ax(s,axis,origin):
    return s.rotate((0,90,0) if axis=='X' else ((-90,0,0) if axis=='Y' else ((180,0,0) if axis=='NZ' else (0,0,0)))).translate(origin)

def snap_pin(grip,r=2.,cap=3.5):
    """Flat-sided pin; head, shank and split nose share a 3 mm print face."""
    s=cyl(0,0,-1.8,cap,1.8)+cyl(0,0,-.05,r,grip+.32)
    s+=cyl(0,0,grip+.24,r+.48,.62)
    s+=b.M.cylinder(1.4,r+.48,r-.35,circular_segments=48).translate((0,0,grip+.84))
    s-=box(-.5,-4,max(.6,grip-7),1,8,12)
    return s^box(-cap-1,-PIN_THICKNESS/2,-2,2*cap+2,PIN_THICKNESS,grip+6)

def pin_bore(r,z,length,clear=PIN_CLEARANCE,round_bearing=False):
    bore=cyl(0,0,z,r+clear,length)
    if not round_bearing:
        bore=bore^box(-r-clear-1,-PIN_THICKNESS/2-clear,z-1,2*r+2*clear+2,PIN_THICKNESS+2*clear,length+2)
    return bore

def connection(ids,origin,axis,grip,group,label,r=2.,cap=3.5):
    id=f'R{len(JOINTS)+1:02}'
    pivot='free-running pivot' in label
    # Key static joints; retain circular running bores on moving jaw parts.
    for part,lo,hi,fillrad in ids:
        fill=ax(cyl(0,0,lo,fillrad,hi-lo),axis,origin)
        bore=ax(pin_bore(r,lo-.2,hi-lo+.4,round_bearing=pivot and part!='C04'),axis,origin)
        setpart(part,(P[part]['s']+fill)-bore)
    s=ax(snap_pin(grip,r,cap),axis,origin)
    ori=(0,-90,0) if axis=='X' else ((90,0,0) if axis=='Y' else ((180,0,0) if axis=='NZ' else (0,0,0)))
    add(id,label+' - flat split push pin',s,'mech',group,orientation=ori)
    P[id]['flat_pin_axis']=axis
    JOINTS.append(dict(id=id,connection=label,parts=[x[0] for x in ids],axis=axis,origin=list(origin),grip_mm=grip,pin_profile='Circle with two parallel flats',pin_width_mm=2*r,pin_thickness_mm=PIN_THICKNESS,clearance_per_side_mm=PIN_CLEARANCE,hole_width_mm=2*(r+PIN_CLEARANCE),hole_flat_spacing_mm=PIN_THICKNESS+2*PIN_CLEARANCE,round_running_bearing_parts=[x[0] for x in ids if pivot and x[0]!='C04'],retention='Flat split nose snaps beyond far face; flat cap is insertion stop. Keyed static hole; circular moving bearing only at jaw pivots.'))
    return id

def base():
    # Separate rings, with one continuous downward/upward sleeve channel.
    bottom=cyl(0,0,0,80,14,160)-cyl(0,0,-1,69,16,160)
    bottom-=cyl(0,0,3,77.4,12,160)-cyl(0,0,2,72,14,160)
    bottom-=box(-6,-83,4,12,16,7)
    bottom+=cyl(0,0,0,69.2,2)-cyl(0,0,-1,66.5,4)
    top=cyl(0,0,93,83,20,160)-cyl(0,0,92,69,22,160)
    top-=cyl(0,0,92,77.4,9,160)-cyl(0,0,91,72,15,160)
    top-=cyl(0,0,103,79.4,11,160)
    setpart('C09',bottom,'Bottom rim - 5.4 mm sleeve channel')
    add('B01','Top rim - sleeve channel and stem-support ledge',top,'pipe')
    # Open radial top support: ring, three spokes and a central stem seat.
    soil=cyl(0,0,107.9,79,3.2,160)-cyl(0,0,107.8,67.5,3.5,160)
    soil+=cyl(0,-18,107.9,32,3.2)-cyl(0,-18,107,10,5)
    for a in np.radians([35,145,270]):
        x,y=66*np.cos(a),66*np.sin(a)
        spoke=(cyl(0,-18,107.9,6,3.2)+cyl(x,y,107.9,6,3.2)).hull()
        soil+=spoke-cyl(0,-18,107,10,5)
    # Keep the stem's original world height: support is under the 107.8 flange.
    soil=soil.translate((0,0,-4.5))
    # Ledge posts bridge to the new lower support plane.
    for a in np.radians([35,145,270]):
        x,y=66*np.cos(a),66*np.sin(a)
        top+=cyl(x,y,101.4,5,1.6)
        soil+=cyl(x,y,103.4,5,3.2)
    setpart('B01',top)
    setpart('C11',soil,'Open three-spoke stem support - optional cardboard soil infill')
    # Open rectangular electronics frame, with ribs instead of a solid disk.
    tray=(box(-40,-56,4,80,92,3.6)-box(-36,-52,3,72,84,6))
    tray+=box(-40,-30,4,80,5,3.6)+box(-40,24,4,80,5,3.6)
    tray+=box(-40,-56,4,42,5,3.6)
    for x,y in [(-48,-40),(48,-40),(0,61)]:
        end=(max(-36,min(36,x)),max(-51,min(32,y)))
        tray+=(cyl(x,y,4,5,3.6)+cyl(*end,4,5,3.6)).hull()
        bottom+=(cyl(x,y,7.8,5,4)+cyl(x*1.17,y*1.17,7.8,5,4)).hull()
    # Board edge channels: press in along X, clip rails retain the PCB edges.
    for y in [-29,25]:
        tray+=box(-36,y-2,7.5,72,2,9)
        tray+=box(-36,y-1,14.4,72,2.3,1.2)
    tray+=box(-40,-56,7.5,42,2,11)+box(-40,-30.8,7.5,42,2,11)
    setpart('C10',tray,'Open electronics tray with PCB edge rails')
    setpart('C09',bottom)
    for i,(x,y) in enumerate([(-48,-40),(48,-40),(0,61)]):
        connection([('C10',0,3.6,3),('C09',3.8,7.8,3)],(x,y,4),'Z',7.8,'fixed','Bottom tray to rim '+str(i+1))
    for i,a in enumerate(np.radians([35,145,270])):
        x,y=66*np.cos(a),66*np.sin(a)
        # Insert upward from underside of top rim mount pad.
        connection([('B01',0,2,3.2),('C11',2,5.2,3.2)],(x,y,101.4),'Z',5.2,'fixed','Top support to rim '+str(i+1))
    for i,(x,y) in enumerate([(-26,-18),(26,-18),(0,8)]):
        connection([('C11',0,4.4,3.4),('C12',4.4,9.4,3.4)],(x,y,103.4),'Z',9.4,'fixed','Stem foot '+str(i+1))
    for a in np.radians([35,145,270]):
        x,y=66*np.cos(a),66*np.sin(a)
        setpart('B01',P['B01']['s']-cyl(x,y,99.2,3.7,2.21))
    # Lighten only the middle of the thick stem; keep both structural flanges.
    ps=[]
    for t in np.linspace(.08,.90,70):ps.append([3*np.sin(t*4),-18-41*t-8*np.sin(t*np.pi),107+135*t])
    setpart('C12',P['C12']['s']-tube(ps,np.linspace(16.0,11.9,len(ps)),64))
    # Leaf tangs have compliant friction ribs, not adhesive retention.
    for id,sg,z,y in [('C13',-1,162,-40),('C14',1,184,-48)]:
        x=17 if sg>0 else -29
        s=P[id]['s']-box(x+1,y-.45,z-3,9,.9,6)
        for yy in [y-3,y+3]:s+=box(x+2,yy-.38,z-1.4,7,.76,2.8)
        setpart(id,s,P[id]['name']+' - split press-fit tang')
    # Existing display bezel grips the cardboard through two push pins and rear clamps.
    for i,x in enumerate([-29,29]):
        connection([('C'+str(16+i),0,9,3.5),('C15',18.9,23.9,3.5)],(x,56.5,52),'Y',23.9,'fixed','Display sleeve sandwich '+str(i+1))
    # Two side sliding wedges retain common display PCB edges without foam/glue.
    for i,x in enumerate([-22.5,22.5]):
        s=box(x-.5,67.3,41,1,2,22)+box(x-1,66.7,41,2,1,22)
        setpart('C15',P['C15']['s']-box(x-1.1,66.6,40.9,2.2,2.8,22.2))
        add('D'+str(i+1).zfill(2),'Display PCB edge shim '+str(i+1),s,'mech',orientation=(90,0,0))

def teeth():
    sockets=[]
    for upper in [True,False]:
        angles=[5,25,45,65,115,135,155,175] if upper else [15,35,55,125,145,165]
        jaw='C01' if upper else 'C02'
        for i,a in enumerate(np.radians(angles)):
            id=('U' if upper else 'L')+f'{i+1:02}'
            origin=np.array([(72 if upper else 68)*np.cos(a),68*np.sin(a),28 if upper else -1])
            # Preserve the curved fang silhouette in its radial plane, flatten both faces.
            old=P[id]['s'].translate(-origin).rotate((0,0,-np.degrees(a))).rotate((0 if upper else 180,0,0))
            crown=old^box(-30,-1.5,-40,60,3,40)
            # Flat split root, 3 mm thick, with small compressible retention barbs.
            root=box(-2.5,-1.5,-.4,5,3,7.4)
            for sg in [-1,1]:
                pts=np.array([[sg*2.5,4.4],[sg*3.05,5.1],[sg*2.5,6.4]])
                root+=b.m.CrossSection([pts if sg>0 else pts[::-1]]).extrude(3).rotate((90,0,0)).translate((0,1.5,0))
            root-=box(-.5,-2,1.6,1,4,7)
            tooth=crown+root
            s=mouth.install(tooth,a,upper,origin)
            setpart(id,s,('Upper' if upper else 'Lower')+' flat snap-in tooth '+str(i+1))
            # This rotation makes the entire 3 mm fang lie broad-face down.
            P[id]['orientation']=(90 if upper else -90,0,-np.degrees(a))
            # Orientation uses an explicit transform during export; Euler order otherwise differs.
            P[id]['flat_tooth_angle_deg']=float(np.degrees(a));P[id]['flat_tooth_upper']=upper
            fill=mouth.install(cyl(0,0,0,3.4,7.3),a,upper,origin)
            cut=box(-2.7,-1.7,-.2,5.4,3.4,7.5)+box(-3.2,-1.7,4.4,6.4,3.4,2.2)
            setpart(jaw,(P[jaw]['s']+fill)-mouth.install(cut,a,upper,origin))
            sockets.append(dict(id=id,jaw=jaw,origin=origin.tolist(),angle_deg=float(np.degrees(a)),upper=upper,thickness_mm=3,root_width_mm=5,slot_width_mm=5.4,barb_width_mm=6.1,detent_pocket_width_mm=6.4,root_length_mm=7))
    (v.ROOT/'validation/tooth_sockets.json').write_text(json.dumps(sockets,indent=2),encoding='utf-8')

def tongue():
    # Retain the original root's mounting feet but remove its first flesh section.
    old=P['A01']['s']
    mount=box(-24,8,-8.6,10,19,3.3)+box(34,8,-8.6,8.5,19,3.3)
    mount+=box(-20,16,-5.4,6,7,9)+box(34,16,-5.4,6,7,9)
    mount+=box(-20,18,1,60,5,2)
    mount+=box(-3,12,2.8,20,6,3.5)
    sock=box(-10,-8,-4.8,20,12.5,9.6)-box(-8.3,-8.2,-2.7,16.6,14,5.4)
    # Rear stop and split sides retain the root tongue tenon by interference ribs.
    sock+=box(-10,-9,-4.8,20,1.5,9.6)
    mount+=sock.transform(v.section_matrix(0,0))
    mount-=tube([v.point(0,0,[0,y,-6]) for y in [-9,5,17]],2.2,32)
    add('A00','Snap-in tongue mounting saddle',mount,'mech','lower')
    for i in range(7):
        id=f'A{i+1:02}'
        width=[36,36,34,32,29,25,20][i]
        body=sphere((0,11,.3),1,(width/2,7,4.2),64)
        body+=box(-5,3,-2.4,10,17,4.8)
        # A 1.8 mm wide flat spine starts every section on the same print plane.
        body+=(box(-18,5,-2.4,1.8,12,4.8)+box(-width/2+1,5,-2.4,3,12,4.8)).hull()
        for y in [7.,10.,13.,16.]:
            w=width*.34*math.sqrt(max(.1,1-((y-11)/7)**2))
            body+=tube([[-w,y,2.4],[0,y+.45,4.1],[w,y,2.4]],[.65,.75,.65],12)
        rng=np.random.default_rng(70+i)
        for _ in range(26):
            x,y=rng.uniform(-width*.34,width*.34),rng.uniform(6.5,15.5)
            z=.3+4.2*math.sqrt(max(.01,1-(x/(width/2))**2-((y-11)/7)**2))
            body+=sphere((x,y,z-.12),.55,(1,1,.75),12)
        if i<6:body-=cx(-19,22,0,6.8,10.7)+cx(8.3,22,0,6.8,10.7)
        h=b.M()
        if i>0:
            for x,ln in [(-15.6,6.6),(9.,4.6)]:h+=cx(x,0,0,6,ln)
            h+=box(-15.6,2,-2.3,29.2,5,4.6)
            skirt=ax(b.M.cylinder(2.4,4.8,6,circular_segments=48),'X',(-18,0,0))
            skirt-=ax(b.M.cylinder(2.42,3.5,2.2,circular_segments=48),'X',(-18.01,0,0))
            h+=skirt+box(-18,3.5,-2.3,2.5,3.5,4.6)
            h-=cx(-19,0,0,2.2,38)
            # Moving stop tab begins at X=-12.6. Leave 0.8 mm behind it
            # instead of the previous 0.5 mm, without changing stop angles.
            h-=v.arc_wedge(0,0,1.7,6.8,-145,-80,-13.4,4.5)
            body-=cx(-9.2,0,0,3.8,18.4)
        else:
            tenon=box(-8,-7,-2.4,16,12,4.8)-box(-.45,-7.2,-3,.9,10.2,6)
            for x in [-8,8]:tenon+=box(x-.35,-4,-1.7,.7,7,3.4)
            body+=tenon
        if i<6:
            h+=cx(-8.6,22,0,3.05,17.2)+box(-8.6,16,-2.3,17.2,6,4.6)
            h+=v.arc_wedge(22,0,2.5,6,-100,-80,-12.6,11.6)
            # Continuous integral axle, 0.4 radial and axial running clearance.
            h+=cx(-18,22,0,1.8,33.6)
            h+=ax(b.M.cylinder(2,3.1,1.8,circular_segments=48),'X',(-18,22,0))
            h+=ax(b.M.cylinder(1.4,1.8,3.1,circular_segments=48),'X',(13.999,22,0))
            h+=cx(15.399,22,0,3.1,.6)
        else:body+=sphere((0,20,0),1,(7,6,3),48)
        body+=h
        if i>0:body-=cx(-9.2,0,0,3.8,18.4)
        for zz,rr in [(-6.,.8),(5.8,1.1)]:
            body+=cy(0,4.4,zz,rr+1.05,13.2)+box(-2.1,5,min(zz,0),4.2,12,abs(zz)+.1)
            body-=cy(0,3.8,zz,rr,14.4)
        # Rounded entry edges remain open for threading after printing.
        setpart(id,body,'Captive print-in-place tongue section '+str(i+1))
        P[id].update(group='section',section_index=i,orientation=(0,-90,0),print_assembly='PIP_TONGUE')
    fixed=P['A01']['s'].transform(v.section_matrix(0,0))
    flesh=fixed^box(-40,19,0,90,40,35)
    clearance=union([flesh.translate(o) for o in [(0,0,0),(.25,0,0),(-.25,0,0),(0,-.25,0),(0,0,-.25),(0,0,.25)]])
    setpart('A00',P['A00']['s']-clearance-box(-3,18.5,14.7,20,1,3))
    # Eliminate old unused holes at y=18 and make root/fairlead pushes at y=12.
    for x in [-19,39]:setpart('C02',P['C02']['s']+cyl(x,18,-13,2.1,4))
    for i,x in enumerate([-19,39]):
        connection([('C02',0,22 if x>0 else 4,3.5),('A00',22.4 if x>0 else 4.4,25.7 if x>0 else 7.7,3.5)],(x,12,-31 if x>0 else -13),'Z',25.7 if x>0 else 7.7,'lower','Tongue saddle '+str(i+1))
    connection([('C02',0,4,3.2),('A09',4.4,7.4,3.2)],(41,1,-13),'Z',7.4,'lower','Tendon guide')

def mechanics():
    for i,(x,y) in enumerate([(-17,-59),(17,-59),(0,-42)]):
        ztop=255 if y==-59 else 247
        connection([('C12',ztop-241,ztop-236,3.4)],(x,y,ztop),'NZ',ztop-236,'fixed','Head frame to stem '+str(i+1))
        fill=cyl(x,y,-23.6,3.4,ztop-241.4)
        bore=pin_bore(2,-24,ztop-241+.2).translate((x,y,0))
        setpart('C04',(P['C04']['s']+fill)-bore)
        setpart('C12',P['C12']['s']-cyl(x,y,233.4,2.7,2.61))
        JOINTS[-1]['parts'].append('C04')
    for i,(x,y) in enumerate([(-48,20),(48,20),(0,-64)]):
        z0=9 if x else 15.6
        connection([('G00',0,19.6-z0,3.4),('C01',20-z0,25-z0,3.5)],(x,y,z0),'Z',25-z0,'upper','Skull to carrier '+str(i+1))
    # Smooth, captured printed pivots; moving bearings retain 0.2 mm radial play.
    connection([('C04',0,8,3),('G00',9,15,3)],(45,-50,8),'X',15,'head','Upper right free-running pivot')
    connection([('C04',0,8,3),('C02',9,15,3)],(45,-50,-32),'X',15,'head','Lower right free-running pivot')
    connection([('C02',0,6,3),('G02',6.4,12.4,3),('C04',13.4,21.4,3)],(-51.4,-50,-32),'X',21.4,'head','Lower left free-running pivot')
    for i,a in enumerate(np.radians([0,120,240])):
        y=-50+10*np.cos(a);z=-32+10*np.sin(a)
        connection([('C02',0,6,3.5),('G02',6.4,12.4,3.5)],(-51.4,y,z),'X',12.4,'lower','Sector to jaw '+str(i+1),r=1.8,cap=2.8)
    for i,(y,z) in enumerate([(-71,-20),(-68,-40)]):
        connection([('C18',0,18,3.4),('C04',19,27,3.4)],(-57,y,z),'X',27,'head','Removable cheek '+str(i+1))
    # Integrate pinion + spacer into the upper carrier: no tiny threaded stack.
    rotor=P['G00']['s']+P['G01']['s']+P['G03']['s']+cx(-45.5,-50,8,7,8.5)
    rotor-=cx(-52,-50,8,3.2,20)
    # Compact custom hub, with a replaceable keyed spline insert.
    rotor+=cx(-39,-50,8,6.4,11.5)
    rotor-=ax(cyl(0,0,0,5.3,11.3,6),'X',(-38.6,-50,8))
    setpart('G00',rotor,'Upper carrier with integral pinion and custom keyed drive hub')
    del P['G01'];del P['G03']
    # Cheek becomes the stationary axial keeper, 0.4 mm clear of carrier face.
    s=P['C18']['s']+cx(-55,-50,8,6.8,3.2)
    setpart('C18',s,'Push-pin cheek and MG995 horn axial keeper')
    # Drum receives its own small custom spline insert, independent of stock horns.
    s=P['A08']['s']
    for z in [-25.8,-13.8]:s+=cx(32,-13,z,1.4,6)
    setpart('A08',s,'MG90S drum with custom keyed drive hub')
    keep=beamx((-1,-6),(-13,-19.8),3.4,38.4,2)+cx(38.4,-13,-19.8,5,2)
    setpart('A09',P['A09']['s']+keep,'Push-in fairlead and MG90S horn axial keeper')
    # Clips span the servo case along X, clear of the horn plane and jaw sweep.
    big=box(-29.8,-42,18.25,42.1,8,2)
    for x in [-29.8,10.5]:big+=box(x,-42,-6.8,1.8,8,27.1)
    big+=box(-29.8,-42,-6.9,3.3,8,1.2)+box(9,-42,-6.9,3.3,8,1.2)
    add('S01','MG995 removable press-over cradle clip',big,'mech','head',orientation=(90,0,0))
    slots=box(-30,-42.2,-5.5,2.2,8.4,28)+box(10.3,-42.2,-5.5,2.2,8.4,28)
    setpart('C04',P['C04']['s']-slots-box(8.8,-42.2,-7,3.7,8.4,1.5)-box(-30,-42.2,-7,3.7,1.4,1.6))
    small=box(-.8,1,-30.8,33,3.5,1.6)
    for x in [-.8,30.4]:small+=box(x,1,-30.8,1.8,3.5,23.4)
    small+=box(-.8,1,-8.8,3.6,3.5,1.4)+box(28.6,1,-8.8,3.6,3.5,1.4)
    add('S02','MG90S removable underside case retainer',small,'mech','lower',orientation=(90,0,0))
    setpart('C02',P['C02']['s']-box(-1,.8,-31,2.2,3.9,22.2)-box(30.2,.8,-31,2.2,3.9,22.2))
    # Offset the drum to accommodate the custom spline insert and keeper.
    for id in ['A08','A09','R14']:setpart(id,P[id]['s'].translate((4,0,0)))
    for j in JOINTS:
        if j['id']=='R14':j['origin'][0]+=4
    setpart('C02',P['C02']['s']+cyl(41,1,-13,2.2,4)+box(35,-6,-13,14,12,4))
    setpart('C02',P['C02']['s']-pin_bore(2,-15,10).translate((45,1,0)))
    # Custom hub replaces the long horn pocket and its large sweep cut.
    hub=cx(30.4,-13,-19.8,6,7.2)
    spool=P['A08']['s']+hub
    spool-=cx(30.2,-13,-19.8,4.3,10.2,6)
    setpart('A08',spool)
    sweep=cx(35.6,-13,-19.8,12,7)
    setpart('C02',P['C02']['s']-sweep)
    setpart('A09',P['A09']['s']-sweep)
    # The fixed guide keeper sits beside the lower tray, separated by 0.3 mm.
    fixed=P['A09']['s']
    pocket=union([fixed.translate((dx,dy,dz)) for dx,dy,dz in [(0,0,0),(.3,0,0),(-.3,0,0),(0,.3,0),(0,-.3,0),(0,0,-.3)]])
    setpart('C02',P['C02']['s']-pocket)
    setpart('A09',P['A09']['s']-pin_bore(2,-16,14).translate((45,1,0))-cyl(45,1,-15.2,3.7,2.21)-cyl(45,1,-5.6,2.7,5))
    # Shallow swept reliefs for the longer snap noses and low heads.
    for target,fasteners in [('C04',['R25','R26','R20']),('C18',['R24','R26'])]:
        clear=[]
        for id in fasteners:
            for q in np.linspace(0,50,26):
                s=v.jaw_pose(P[id]['s'],q,P[id]['group']=='upper')
                clear.extend([s,s.translate((-.25,0,0)),s.translate((.25,0,0))])
        setpart(target,P[target]['s']-union(clear))
    # Minor ledge clearances beneath mounting-pin heads and a longer horn cup.
    setpart('G00',P['G00']['s']-cyl(-48,20,6.9,3.7,2.11))
    clear=[]
    for q in np.linspace(0,50,51):
        cu=v.jaw_pose(P['G00']['s'],q,True)
        clear.extend([cu,cu.translate((.2,0,0)),cu.translate((0,0,-.2))])
    setpart('C04',P['C04']['s']-union(clear))
    # Flat clearance beneath the cover push-pin heads.
    for y,z in [(-71,-20),(-68,-40)]:setpart('C18',P['C18']['s']-cx(-62,y,z,3.7,5))
    custom_hubs()

# Diameters and heights use the user's measurements; spline flanks/counts
# remain trial fits because no complete manufacturer spline drawing is known.
# A rounded triangular spline approximates the tooth flanks; it is NOT a
# manufacturer-certified spline standard or a demonstrated high-torque joint.
def spline_cutter(teeth,major,minor,length,clearance=0):
    pts=[]
    for i in range(teeth):
        for off,r in [(-.5,minor),(-.25,major),(.25,major)]:
            a=(i+off)*2*np.pi/teeth
            pts.append([(r+clearance)*np.cos(a),(r+clearance)*np.sin(a)])
    return b.m.CrossSection([np.array(pts)]).extrude(length)

def spline_insert(large,offset=0,teeth=None):
    n=teeth or (25 if large else 21)
    # A replaceable hex exterior carries torque into the printed mechanism.
    r=5.26 if large else 4.26;ln=11.1 if large else 9.8
    body=cyl(0,0,0,r,ln,6)
    major,minor=(3.,2.68) if large else (2.4,2.12)
    if large:
        cut=spline_cutter(n,major,minor,3.8,offset).translate((0,0,7.4))
        cut+=b.M.cylinder(.45,minor-.05+offset,major+.25+offset,circular_segments=61).rotate((0,0,1.37)).translate((0,0,ln-.45))
    else:
        cut=spline_cutter(n,major,minor,4.9,offset).translate((0,0,-.1))
        cut+=b.M.cylinder(.4,major+.25+offset,minor-.05+offset,circular_segments=61).rotate((0,0,1.37)).translate((0,0,-.01))
    return body-cut

def custom_hubs():
    add('H01','Custom MG995 spline insert - trial 25T 6 mm',ax(spline_insert(True),'X',(-38.6,-50,8)),'gold','upper',orientation=(0,-90,0))
    add('H02','Custom MG90S spline insert - trial 21T 4.8 mm',ax(spline_insert(False),'X',(30.4,-13,-19.8)),'gold','spool',orientation=(0,90,0))
    fits=[]
    for large in [True,False]:
        for count_index,n in enumerate([25,24] if large else [21,20]):
            for i,diam in enumerate([5.6,5.85,6.1] if large else [4.6,4.85,5.1]):
                id=('F1' if large else 'F2')+str(count_index*3+i+1)
                off=(diam-(6 if large else 4.8))/2
                s=spline_insert(large,off,n)
                for j in range(i+1):s-=cyl(-1.5+j*1.5,0,0 if large else 9.3,.35,.5)
                if count_index:s-=box(-1.5,1.3,0 if large else 9.3,3,.6,.5)
                add(id,('MG995' if large else 'MG90S')+f' trial {n}T / {diam:.2f} mm bore',s,'mech','test',orientation=(0,0,0) if large else (180,0,0))
                fits.append(dict(id=id,servo='MG995' if large else 'MG90S',trial_teeth=n,major_diameter_mm=diam,identification=f'{i+1} dots'+(' plus bar' if count_index else '')))
    (v.ROOT/'validation/custom_hubs.json').write_text(json.dumps(dict(status='Custom printed hubs; user supplied diameter ranges and exposed heights; spline tooth counts and flank shape remain unconfirmed',user_measurements=dict(MG995=dict(diameter_range_mm=[5.5,6],height_mm=4),MG90S=dict(diameter_range_mm=[4.5,5],height_range_mm=[4.5,5])),trial_profiles=dict(MG995=dict(teeth=25,major_diameter_mm=6,minor_diameter_mm=5.36),MG90S=dict(teeth=21,major_diameter_mm=4.8,minor_diameter_mm=4.24)),samples=fits,retention='Removable stationary keepers constrain axial withdrawal; hex insert exteriors carry torque into carrier and drum.',physical_tested=False),indent=2),encoding='utf-8')

def coupons():
    for id in ['T01','T02','T03','A10']:
        if id in P:del P[id]
    block=box(0,0,0,54,18,8)
    for i,clear in enumerate([.15,.2,.25]):
        block-=pin_bore(2,-1,10,clear).translate((9+18*i,9,0))
        for j in range(i+1):block-=cyl(7+18*i+2*j,3,7.5,.55,1)
    add('T01','Flat pin coupon - one two three dots = 0.15 0.20 0.25 mm per side',block,'mech','test')
    add('T02','Flat push-pin coupon key - 8 mm grip',snap_pin(8),'mech','test')
    P['T02']['flat_pin_axis']='Z'
    # Use two complete production sections so the coupon tests the exact
    # bearing, capture heads and printing supports of the finished tongue.
    male=P['A06']['s']
    female=P['A07']['s']
    add('T04','Print-in-place hinge sample - axle side',male,'tongue','test',orientation=(0,-90,0))
    add('T05','Print-in-place hinge sample - captive knuckle side',female,'tongue','test',orientation=(0,-90,0))
    P['T04']['print_assembly']='PIP_TEST';P['T05']['print_assembly']='PIP_TEST'
    # Same flat tooth root and retention pocket, three entry clearances.
    block=box(0,0,0,48,14,9)
    for i,clear in enumerate([.15,.2,.25]):
        cut=box(-2.5-clear,-1.5-clear,-.2,5+2*clear,3+2*clear,7.5)+box(-3.2,-1.5-clear,4.4,6.4,3+2*clear,2.2)
        block-=cut.rotate((180,0,0)).translate((8+16*i,7,9))
        for j in range(i+1):block-=cyl(6+16*i+2*j,2.5,8.5,.5,1)
    add('T03','Flat tooth socket fit coupon',block,'mech','test')

def tendon_entry_relief():
    # The offset drum approaches the root diagonally. Relieve this shared
    # entry in both saddle and tongue so the free tendon does not rub an edge.
    relief=tube([[39,-1,-3],v.point(0,0,[0,5,-6]),v.point(0,0,[0,7,-6])],1.1,32)
    setpart('A00',P['A00']['s']-relief)
    matrix=v.section_matrix(0,0);rot=matrix[:,:3];offset=matrix[:,3]
    inverse=np.column_stack([rot.T,-rot.T@offset])
    setpart('A01',P['A01']['s']-relief.transform(inverse))

def revise():
    before={id:p['s'].volume()/1000 for id,p in P.items()}
    base();teeth();tongue();mechanics();tendon_entry_relief();coupons()
    for p in P.values():
        parts=[s for s in p['s'].decompose() if s.volume()>1e-6]
        assert len(parts)==1,(p['id'],[(s.volume(),s.bounding_box()) for s in parts])
    (v.ROOT/'validation/press_fit_joints.json').write_text(json.dumps(JOINTS,indent=2),encoding='utf-8')
    after={id:p['s'].volume()/1000 for id,p in P.items()}
    report=dict(previous_printed_solid_volume_cm3=sum(before.values()),new_printed_solid_volume_cm3=sum(after.values()),change_percent=100*(sum(after.values())/sum(before.values())-1),before=before,after=after,note='CAD solid volumes, not slicer filament estimates. Does not include infill, supports, brims or purge. Sleeve is user-cut sheet stock.',physical_tested=False)
    (v.ROOT/'validation/material_comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
