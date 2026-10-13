"""Reproduce the approved Design-1 scientific SVG from source-indexed results.
All network/control geometry is native SVG; only genuine scientific specimens
are embedded images. No concept PNG is embedded in the scientific figure.
"""
from __future__ import annotations
import base64, csv, hashlib, html, json, math, shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import cairosvg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
RAW=OUT/'source_files'
SOURCE_INPUTS=json.loads((OUT/'SOURCE_INPUTS.json').read_text())
ASSET=OUT/'assets'; ASSET.mkdir(exist_ok=True)
W,H=1800,1480
WIDTH_MM=522.50787/72.27*25.4  # measured C&G runtime textwidth; geometry margins override declared467.75pt
HEIGHT_MM=WIDTH_MM*H/W
UID='0571e6db30c84b1593bc55a8e145a430'
BUID='3c83796ca5f043f1beb8044dd2e51a0d'
REND=RAW
PRED=RAW/'C3_six_view_composite.png'
ATLAS=RAW/'native_gc3_UV_atlas.png'
UNSEEN=RAW/'unseen004.png'
C={'ink':'#263239','gray':'#65747B','hair':'#CCD5D8','pale':'#F0F3F4','teal':'#117C73','teal_pale':'#E7F3F0','white':'#FFFFFF'}
FONT=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
FONT_BOLD=FONT.with_name('DejaVuSans-Bold.ttf')
FONT_ITALIC=FONT.with_name('DejaVuSans-Oblique.ttf')
rows=[]; image_slots=[]; measurements=[]; parts=[]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def register(name,source,display,uid,method,camera,op,crop='',rotation=0):
    with Image.open(source) as im: src_res=f'{im.width}x{im.height}'
    with Image.open(display) as im: dst_res=f'{im.width}x{im.height}'
    rows.append({'asset_id':name,'source_path':SOURCE_INPUTS[Path(source).name]['original_path'],'packaged_source_path':str(source),'display_path':str(display),'object_uid':uid,'method':method,'camera_view_id':camera,'source_resolution':src_res,'display_resolution':dst_res,'operation':op,'crop_box_xyxy':crop,'native_saved_rotation_deg':rotation,'source_sha256':sha(source),'display_sha256':sha(display)})
    return Path(display)
def copy_asset(name,source,uid,method,camera):
    dst=ASSET/f'{name}.png'; shutil.copy2(source,dst)
    return register(name,source,dst,uid,method,camera,'Unchanged saved PNG; SVG uniform scaling; alpha composited over white at render time')

ref=copy_asset('reference014',RAW/'reference014.png',UID,'Frozen Fresh C reference / embedding conditioning','014')
normal=copy_asset('normal014_representative',RAW/'normal014.png',UID,'Representative raw geometry source; not transformed six-view mosaic','014')
depth_src=RAW/'depth014.png'
with Image.open(depth_src) as im:
    arr=np.asarray(im).astype(np.float64)
Image.fromarray(np.rint(arr/257).astype('uint8'),'L').save(ASSET/'depth014_display.png')
depth=register('depth014_representative',depth_src,ASSET/'depth014_display.png',UID,'Representative raw geometry source; not exact model tensor','014','Uniform 16-bit→8-bit display conversion round(value/257); no local contrast/color adjustment')
with Image.open(ref) as im: im.getchannel('A').save(ASSET/'mask014_alpha.png')
mask=register('mask014_representative',RAW/'reference014.png',ASSET/'mask014_alpha.png',UID,'Representative foreground geometry mask','014','Exact reference014 alpha extraction; no threshold or smoothing')
evidence=json.loads((OUT/'source_audit/CAMERA_AND_SCALE_EVIDENCE.json').read_text())
caminfo=evidence['six_output_tiles']
views=[]
with Image.open(PRED) as original:
    assert original.size==(512,768)
    for v in caminfo:
        i=v['tile']; row,col=divmod(i,2); box=(col*256,row*256,(col+1)*256,(row+1)*256)
        dst=ASSET/f'output_tile{i}_camera{v["raw_camera_id"]}.png'
        original.crop(box).save(dst)
        with Image.open(dst) as tile: assert np.array_equal(np.asarray(tile),np.asarray(original)[box[1]:box[3],box[0]:box[2]])
        views.append(register(f'output_tile{i}',PRED,dst,UID,'Fresh C frozen C3 / native_gc3',v['raw_camera_id'],'Exact saved tile crop; no recoloring, new rotation or detail correction; native order preserved',json.dumps(box),v['already_applied_inplane_rotation_deg']))
atlas=copy_asset('bake_native_gc3_uv_atlas',ATLAS,BUID,'Selected Bake10 native_gc3 actual UV bake','UV atlas (not a camera)')
# Enlarged standalone bake illustration: exact foreground bounding crop plus12px.
# Only transparent margins are removed; no nontransparent source pixel is lost.
with Image.open(UNSEEN) as source:
    assert source.mode=='RGBA'
    b=source.getchannel('A').getbbox();pad=12
    box=(max(0,b[0]-pad),max(0,b[1]-pad),min(source.width,b[2]+pad),min(source.height,b[3]+pad))
    dst=ASSET/'bake_unseen004_foreground_crop.png';source.crop(box).save(dst)
    with Image.open(dst) as crop: assert np.array_equal(np.asarray(crop),np.asarray(source)[box[1]:box[3],box[0]:box[2]])
unseen=register('bake_native_gc3_unseen004',UNSEEN,dst,BUID,'Selected Bake10 native_gc3 unlit base-color unseen render','004 (unseen camera set 001–011)','Lossless full-foreground crop: alpha bounding box plus12px transparent margin; no pixel changes or enhancement',json.dumps(box))
# Assert corrected reference identity before any diagram generation.
assert evidence['condition_embedding_record']['selected_condition_view']=='014'
assert sha(RAW/'reference014.png')==evidence['condition_embedding_record']['condition_source']['image_file_sha256']['014']
assert sha(ATLAS)=='6ab6b25a0a76a9ed989cfe42b415f679ccee8d2f21993d94d24a62e2d99a0095'
assert sha(UNSEEN)=='5bb8d166243c86da29c3ad0e77d44cdce09307aa1a543b8b17e70fabb607cd87'
logpath=RAW/'C3_residual_trace.json'
log=json.loads(logpath.read_text()); req=[]; caps={'deep':3.,'middle':3.5,'shallow':.8}
for t in range(50):
    s=1.25 if t<17 or t>=33 else 2.5; req.append(s)
    for e in log[str(t)].values(): assert e['scale']==s and e['eff_scale']==min(s,caps[e['depth']])

def add(s): parts.append(s)
def group(i): add(f'<g id="{i}">')
def endgroup(): add('</g>')
def rect(i,x,y,w,h,fill='none',stroke=None,sw=1.6,rx=0):
    add(f'<rect id="{i}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke or C["hair"]}" stroke-width="{sw}"/>')
def path(i,d,color=None,sw=2.8,arrow=True):
    color=color or C['gray']; marker=' marker-end="url(#arrow-teal)"' if color==C['teal'] else ' marker-end="url(#arrow-gray)"'
    add(f'<path id="{i}" d="{d}" stroke="{color}" stroke-width="{sw}" fill="none" stroke-linecap="round" stroke-linejoin="round"{marker if arrow else ""}/>')
def line(i,x1,y1,x2,y2,**kw):path(i,f'M{x1},{y1} L{x2},{y2}',**kw)
def text(i,x,y,s,size=30,color=None,bold=False,anchor='start'):
    color=color or C['ink']; f=ImageFont.truetype(str(FONT_BOLD if bold else FONT),size)
    b=f.getbbox(s,anchor='ls'); width=f.getlength(s); bx=x-(width/2 if anchor=='middle' else width if anchor=='end' else 0)
    measurements.append({'id':i,'text':s,'bbox':[bx+b[0],y+b[1],bx+b[2],y+b[3]],'font_pt':size*WIDTH_MM/W*72/25.4,'kind':'text'})
    add(f'<text id="{i}" x="{x}" y="{y}" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}">{html.escape(s)}</text>')
def mathtext(i,x,y,tokens,size=31,anchor='start',color=None):
    runs=[]; total=0
    for s,sty in tokens:
        fs=round(size*.7) if sty=='sub' else size
        font=ImageFont.truetype(str(FONT_ITALIC if sty in ('italic','sub') else FONT),fs)
        length=font.getlength(s); runs.append((s,sty,fs,length));total+=length
    cursor=x-(total/2 if anchor=='middle' else 0); left=cursor
    add(f'<text id="{i}" fill="{color or C["ink"]}">')
    for s,sty,fs,length in runs:
        yy=y+(size*.19 if sty=='sub' else 0)
        add(f'<tspan x="{cursor:.3f}" y="{yy:.3f}" font-size="{fs}" font-style="{"italic" if sty in ("italic","sub") else "normal"}">{html.escape(s)}</tspan>'); cursor+=length
    add('</text>')
    measurements.append({'id':i,'text':''.join(r[0] for r in runs),'bbox':[left,y-size,cursor,y+size*.22],'font_pt':size*WIDTH_MM/W*72/25.4,'kind':'math'})
def image(i,p,x,y,w,h):
    data=base64.b64encode(p.read_bytes()).decode()
    add(f'<image id="{i}" x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{data}" preserveAspectRatio="xMidYMid meet"/>')
    image_slots.append({'id':i,'asset_file':str(p),'asset_sha256':sha(p),'bbox':[x,y,w,h],'uniform_fit':'meet; no additional crop'})
def node(i,x,y,s,color=None):
    color=color or C['ink'];add(f'<circle id="{i}" cx="{x}" cy="{y}" r="25" fill="white" stroke="{color}" stroke-width="3.2"/>');text(i+'-symbol',x,y+13,s,43,color,False,'middle')

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH_MM:.6f}mm" height="{HEIGHT_MM:.6f}mm" viewBox="0 0 {W} {H}" font-family="DejaVu Sans">')
add('<title>TCAS control on an existing geometry-residual path</title>')
add('<desc>Same-UID reference camera014 and six C3 views; representative geometry sources; distinct reference and geometry paths; native clipping before groupwise residual addition; independent selected Bake10 native UV atlas and unseen004.</desc>')
add('<defs><marker id="arrow-gray" markerUnits="userSpaceOnUse" markerWidth="13" markerHeight="13" refX="11" refY="6.5" orient="auto"><path d="M0,0 L12,6.5 L0,13 Z" fill="#65747B"/></marker><marker id="arrow-teal" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="12" refY="7" orient="auto"><path d="M0,0 L13,7 L0,14 Z" fill="#117C73"/></marker></defs>')
rect('background',0,0,W,H,C['white'],C['white'],0)
group('Inputs')
text('reference-heading',40,65,'Reference image',34,bold=True)
image('reference-camera014',ref,40,115,450,450)
text('reference-camera-label',40,600,'Camera 014 · Fresh C',28,C['gray'])
endgroup()
group('Geometry-conditioning')
text('geometry-heading',40,645,'Geometry conditions',32,bold=True)
for k,(p,label) in enumerate([(normal,'Normal'),(depth,'Depth'),(mask,'Mask')]):
    x=40+k*155;rect('condition-frame-'+label,x,675,130,130,stroke=C['hair'],sw=1.3)
    image('condition-'+label,p,x,675,130,130);text('condition-label-'+label,x+65,839,label,28,C['gray'],False,'middle')
# single thumbnails are representative, exactly qualified in caption and source index
path('geometry-to-adapter','M480,740 H535 V600 H560',sw=2.8)
endgroup()
group('Frozen-diffusion-path')
text('frozen-heading',870,230,'Frozen diffusion U-Net',32,bold=True,anchor='middle')
text('frozen-schematic',870,263,'Schematic feature flow',28,C['gray'],anchor='middle')
rect('frozen-feature',670,290,145,70,C['pale'],C['hair'],1.8,3)
mathtext('frozen-feature-label',742.5,334,[('h','italic'),('frozen','sub')],31,'middle')
line('frozen-to-addition',815,325,931,325,sw=3.0)
node('feature-addition',960,325,'+')
rect('corrected-feature',1030,290,95,70,C['pale'],C['hair'],1.8,3)
mathtext('corrected-feature-label',1077.5,334,[('h','italic'),('out','sub')],31,'middle')
line('addition-to-output-feature',987,325,1025,325,sw=3)
line('feature-to-generated-views',1129,325,1190,325,sw=3)
text('reference-path-label1',480,196,'Reference',28,C['gray'])
text('reference-path-label2',480,230,'conditioning',28,C['gray'])
path('reference-conditioning-path','M492,265 H555 Q570,265 570,276 H742 V285',sw=2.8)
path('feature-input-to-existing-adapter','M695,365 H600 V520 H690 V548',sw=2.2)
text('features-to-adapter-label',614,508,'features',28,C['gray'])
mathtext('residual-addition-equation',628,423,[('h','italic'),('out','sub'),(' = ','normal'),('h','italic'),('frozen','sub'),(' + ','normal'),('s','italic'),('app','sub'),(' × Δh','italic'),('geo','sub')],31)
endgroup()
group('GeoTex-residual-path')
rect('existing-geotex-adapter',565,555,270,90,C['pale'],C['hair'],1.8,3)
text('adapter-label1',700,592,'GeoTex-Adapter',28,bold=True,anchor='middle')
text('adapter-label2',700,628,'Residual path',28,C['gray'],anchor='middle')
line('unscaled-residual-to-multiplier',840,600,931,600,sw=2.8)
mathtext('raw-residual-label',885,566,[('Δh','italic'),('geo','sub')],31,'middle')
endgroup()
group('TCAS-control')
node('residual-scalar-multiplier',960,600,'×',C['teal'])
path('unique-scaled-residual-injection','M960,571 H1135 V375 H960 V354',C['teal'],4.0)
text('scaled-residual-label1',979,492,'Scaled',28,C['teal'])
text('scaled-residual-label2',979,527,'residual',28,C['teal'])
endgroup()
group('Existing-native-wrapper-cap')
rect('existing-native-cap-control',700,770,380,95,C['pale'],C['hair'],2.2,3)
text('existing-wrapper-heading',890,810,'Existing wrapper',30,C['gray'],True,'middle')
mathtext('native-cap-qualifier',890,846,[('Native cap ','normal'),('c','italic'),('l','sub')],28,'middle')
endgroup()
group('Applied-scale')
path('applied-scalar-to-multiplier','M863,767 V672 H960 V629',C['teal'],3.4)
text('applied-scale-heading',980,703,'Applied scale',28,C['teal'])
mathtext('applied-scale-path-label',1035,739,[('s','italic'),('app','sub'),('(t,l)','italic')],29,'middle',C['teal'])
mathtext('scale-clipping-equation',855,925,[('s','italic'),('app','sub'),('(t,l)','italic'),(' = min(','normal'),('s','italic'),('req','sub'),('(t,l)','italic'),(', ','normal'),('c','italic'),('l','sub'),(')','normal')],30,'middle')
text('deep-middle-applied',590,975,'Deep / middle: 1.25 / 2.50 / 1.25',28,C['gray'])
text('shallow-cap-applied',590,1012,'Shallow: applied 0.80 throughout',28,C['gray'])
endgroup()
group('Requested-schedule')
text('schedule-heading',40,905,'TCAS requested schedule',31,C['teal'],True)
x0,x1=80,490; y0=1095
sx=lambda t:x0+(x1-x0)*t/50
sy=lambda v:y0-v*48
line('schedule-axis-x',x0,y0,x1+15,y0,sw=1.7)
line('schedule-axis-y',x0,y0,x0,945,sw=1.7)
# Piecewise-constant cells [t,t+1), for t=0..49: changes exactly at17 and33.
d=f'M{sx(0):.3f},{sy(req[0]):.3f}'
for t in range(50):
    if t and req[t]!=req[t-1]:d+=f' V{sy(req[t]):.3f}'
    d+=f' H{sx(t+1):.3f}'
path('requested-C3-discrete-curve',d,C['teal'],3.4,False)
for idx,(a,b,value,phase) in enumerate([(0,17,1.25,'Early'),(17,33,2.5,'Middle'),(33,50,1.25,'Late')]):
    cx=(sx(a)+sx(b))/2
    text(f'request-value-{idx}',cx,sy(value)-20,f'{value:.2f}',30,bold=True,anchor='middle')
    text(f'phase-{idx}',cx,1136,phase,28,C['gray'],anchor='middle')
    text(f'window-{idx}',cx,1172,f'{a}–{b-1}',28,C['gray'],anchor='middle')
    if idx:line(f'discrete-boundary-tick-{a}',sx(a),y0-5,sx(a),y0+6,sw=1.6,arrow=False)
text('time-axis-zero',x0,y0+30,'0',28,C['gray'],anchor='middle')
text('time-axis-last',sx(49),y0+30,'49',28,C['gray'],anchor='middle')
path('requested-profile-to-cap','M495,1035 H545 V817 H714',C['teal'],2.4)
mathtext('requested-scale-connection-label',621,850,[('s','italic'),('req','sub'),('(t,l)','italic')],28,'middle',C['teal'])
endgroup()
group('Native-cap-accounting')
text('caps-existing-title',40,1220,'Existing native caps',28,C['gray'],True)
for i,(label,value) in enumerate([('Deep','3.00'),('Middle','3.50'),('Shallow','0.80')]):
    x=105+i*175
    text(f'cap-group-{i}',x,1262,label,28,C['gray'],anchor='middle')
    text(f'cap-value-{i}',x,1298,value,28,C['gray'],anchor='middle')
endgroup()
group('Generated-outputs')
text('outputs-heading',1200,65,'Six generated RGB views',34,bold=True)
for i,p in enumerate(views):
    row,col=divmod(i,2);x=1200+col*288;y=115+row*340
    rect(f'output-frame-{i}',x,y,272,272,stroke=C['hair'],sw=1.2)
    image(f'scientific-output-{i}',p,x,y,272,272)
    text(f'output-camera-{i}',x+136,y+309,f'Camera {caminfo[i]["raw_camera_id"]}',28,C['gray'],anchor='middle')
text('output-protocol',1200,1190,'Fresh C · C3',31,bold=True)
text('output-order-note',1200,1230,'Recorded camera order',28,C['gray'])
text('output-shared-uid',1200,1270,'UID 0571e6… · shared with inputs',28,C['gray'])
endgroup()
group('Independent-baked-evaluation')
rect('independent-bake-panel',575,1032,570,440,C['white'],C['hair'],1.6,0)
text('bake-heading',595,1070,'Selected bake studies',31,bold=True)
text('independent-bake-uid',595,1108,'Independent UID 3c8379…',28,C['gray'])
image('actual-native-UV-atlas',atlas,595,1180,185,185)
image('actual-unseen-camera004',unseen,875,1130,245,300)
line('native-UV-to-unseen-render',793,1272,861,1272,sw=2.8)
text('atlas-label',687.5,1405,'Native UV atlas',28,C['gray'],anchor='middle')
text('unseen-label',997.5,1458,'Unseen render · 004',28,C['gray'],anchor='middle')
endgroup()
add('</svg>')
svg='\n'.join(parts)
(OUT/'fig1_tcas_editable.svg').write_text(svg)
cairosvg.svg2pdf(bytestring=svg.encode(),write_to=str(OUT/'fig1_tcas.pdf'))
cairosvg.svg2png(bytestring=svg.encode(),write_to=str(OUT/'fig1_tcas_preview.png'),output_width=2700)
cairosvg.svg2png(bytestring=svg.encode(),write_to=str(OUT/'fig1_tcas_actual_size.png'),output_width=round(WIDTH_MM/25.4*96))
cairosvg.svg2png(bytestring=svg.encode(),write_to=str(OUT/'fig1_tcas_half_size.png'),output_width=round(WIDTH_MM/25.4*48))
cairosvg.svg2png(bytestring=svg.encode(),write_to=str(OUT/'fig1_tcas_164mm_check.png'),output_width=round((467.75/72.27*25.4)/25.4*96))
with (OUT/'FIG1_SOURCE_INDEX_FINAL.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
# Companion records support reproducibility/editability checks, not author approval.
(OUT/'SVG_ELEMENT_MEASUREMENTS.json').write_text(json.dumps({'physical_width_mm':WIDTH_MM,'physical_height_mm':HEIGHT_MM,'canvas':[W,H],'text':measurements,'image_slots':image_slots,'discrete_requested_trace':req,'transition_steps':[17,33]},indent=2)+'\n')
root=ET.fromstring(svg);ns={'s':'http://www.w3.org/2000/svg'}
report={'native_text_elements':len(root.findall('.//s:text',ns)),'native_paths':len(root.findall('.//s:path',ns)),'native_groups':len(root.findall('.//s:g',ns)),'independent_scientific_images':len(root.findall('.//s:image',ns)),'whole_concept_png_embedded':False,'all_source_hashes_recomputed':True,'output_tile_pixel_identity_checked':True,'all_50_steps_checked':True,'minimum_body_label_font_pt':min(t['font_pt'] for t in measurements if t['kind']=='text' and t['id'] not in ['feature-addition-symbol','residual-scalar-multiplier-symbol']),'text_outside_canvas':[t['id'] for t in measurements if t['bbox'][0]<0 or t['bbox'][1]<0 or t['bbox'][2]>W or t['bbox'][3]>H]}
(OUT/'RECONSTRUCTION_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
# One final comparison uses the last verified predecessor; not a scientific result.
prior=Image.open(OUT/'before_final_round.png').convert('RGB')
current=Image.open(OUT/'fig1_tcas_preview.png').convert('RGB')
board=Image.new('RGB',(2420,1100),'white'); draw=ImageDraw.Draw(board)
font=ImageFont.truetype(str(FONT_BOLD),29)
for x,title,im in [(25,'Before final round',prior),(1235,'Final — reference label follows path',current)]:
    im=im.resize((1150,round(im.height*1150/im.width)),Image.Resampling.LANCZOS)
    draw.text((x,20),title,fill=C['ink'],font=font);board.paste(im,(x,85))
board.save(OUT/'FINAL_FIGURE_COMPARISON.png')
print(json.dumps(report,indent=2))
