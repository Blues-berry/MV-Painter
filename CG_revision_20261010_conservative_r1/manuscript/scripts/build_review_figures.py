"""Build compact comparisons from verified research images, without retouching."""
from pathlib import Path
import csv, hashlib, json, base64
import numpy as np
import cairosvg
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'figures'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
PROVENANCE=[]
FRAMES=[]
NAMES={'Reference':'Reference','GFL':'Fixed Low','GFH':'Fixed High','C3':'C3','LLH':'Layer LLH','No Adapter':'No Adapter','Generic Linear':'Linear'}
BAKE_LABELS={'source':'Source','gt':'GT bake','native_default_1x':'1.0 (capped)','native_gfl':'Fixed Low','native_gfh':'Fixed High','budget_fixed_mean':'Fixed Mean','native_gc3':'C3','budget_late16':'Late-high','gen_linear':'Linear'}

def font(size):return ImageFont.truetype(FONT,size)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def actual(path,expected=None):
 path=Path(path)
 if not path.is_absolute():path=ROOT.parent.parent/path
 digest=sha(path)
 if expected and digest!=expected:raise ValueError(f'Source hash mismatch: {path}')
 PROVENANCE.append({'path':str(path),'sha256':digest})
 with Image.open(path) as im:
  rgba=im.convert('RGBA');bg=Image.new('RGBA',rgba.size,'white');bg.alpha_composite(rgba)
  return bg.convert('RGB')
def centered(draw,x,y,width,label,size=25):
 f=font(size);box=draw.textbbox((0,0),label,font=f)
 draw.text((x+(width-box[2]+box[0])/2,y),label,font=f,fill='#253547')
def fit(image,width,height):
 factor=min(width/image.width,height/image.height)
 return image.resize((round(image.width*factor),round(image.height*factor)),Image.Resampling.LANCZOS)
def paste_fit(canvas,image,x,y,width,height):
 image=fit(image,width,height)
 canvas.paste(image,(x+(width-image.width)//2,y+(height-image.height)//2))
 return image.size

def bbox(image):
 a=np.asarray(image,dtype=float)
 edges=np.concatenate([a[:4].reshape(-1,3),a[-4:].reshape(-1,3),a[:,:4].reshape(-1,3),a[:,-4:].reshape(-1,3)])
 background=np.median(edges,axis=0)
 mask=np.max(np.abs(a-background),axis=2)>25
 yy,xx=np.where(mask)
 if not len(xx):return (0,0,image.width,image.height)
 return (int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1)
def shared_frame(images,include=None):
 boxes=[bbox(im) for im in images]
 if include:boxes.append(include)
 w,h=images[0].size
 pad=12 if w>=512 else 6
 return (max(0,min(b[0] for b in boxes)-pad),max(0,min(b[1] for b in boxes)-pad),min(w,max(b[2] for b in boxes)+pad),min(h,max(b[3] for b in boxes)+pad))
def save(image,name):
 image.save(FIG/(name+'.png'))
 # Lossless raster embedded in a vector PDF preserves experimental pixel values.
 data=base64.b64encode((FIG/(name+'.png')).read_bytes()).decode()
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{image.width}" height="{image.height}"><image width="{image.width}" height="{image.height}" href="data:image/png;base64,{data}"/></svg>'
 cairosvg.svg2pdf(bytestring=svg.encode(),write_to=str(FIG/(name+'.pdf')))

def strip(images,labels,tag,frame,detail=None,cell=340):
 ratio=(frame[3]-frame[1])/(frame[2]-frame[0])
 context_h=min(290,max(155,round((cell-16)*ratio)))
 header=46;detail_h=220 if detail else 0
 out=Image.new('RGB',(cell*len(images),header+context_h+detail_h+12),'white');d=ImageDraw.Draw(out)
 d.text((5,8),tag,font=font(22),fill='#253547')
 for col,(im,label) in enumerate(zip(images,labels)):
  centered(d,col*cell,8,cell,label)
  context=im.crop(frame)
  if detail:
   draw=ImageDraw.Draw(context)
   draw.rectangle((detail[0]-frame[0],detail[1]-frame[1],detail[2]-frame[0],detail[3]-frame[1]),outline='#c0373f',width=2)
  paste_fit(out,context,col*cell+6,header,cell-12,context_h)
  if detail:
   paste_fit(out,im.crop(detail),col*cell+12,header+context_h+8,cell-24,detail_h-12)
 return out

def stack(panels,gap=22):
 out=Image.new('RGB',(max(p.width for p in panels),sum(p.height for p in panels)+gap*(len(panels)-1)),'white');y=0
 for p in panels:out.paste(p,(0,y));y+=p.height+gap
 return out

def fresh_panels():
 with (FIG/'FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv').open() as f:rows=list(csv.DictReader(f))
 for old,new in [('fig4','fig4_freshc_context_roi'),('fig5','fig5_freshc_context_roi'),('fig6_color_diagnostic','fig6_color_diagnostic_freshc_context_roi')]:
  groups={}
  for r in rows:
   if r['figure_id']==old:groups.setdefault(r['panel_id'],[]).append(r)
  panels=[]
  for number,group in enumerate(groups.values()):
   tiles=[]
   for r in group:
    im=actual(r['input_path'],r['input_sha256'])
    if r['method']!='Reference':im=im.crop(tuple(map(int,r['tile_bbox'].split(','))))
    tiles.append(im.resize((256,256),Image.Resampling.LANCZOS))
   detail=tuple(map(int,group[0]['crop_bbox'].split(','))) if old=='fig5' else None
   frame=shared_frame(tiles,detail)
   FRAMES.append({'figure':new,'uid':group[0]['object_uid'],'frame':frame,'detail':detail,'rule':'union of all condition foreground extents, shared across methods; unchanged frozen ROI where detail is shown'})
   panels.append(strip(tiles,[NAMES[r['method']] for r in group],f'({chr(97+number)})',frame,detail))
  save(stack(panels),new)

def bake_panels():
 with (FIG/'BAKED_FIGURE_VIDEO_PROVENANCE.csv').open() as f:rows=list(csv.DictReader(f))
 index={(r['uid'],r['method'],int(r['raw_view'])):r for r in rows}
 with (FIG/'BAKED_ASSET_CREDITS.csv').open() as f:credits=list(csv.DictReader(f))
 main=['source','gt','budget_fixed_mean','budget_late16'];panels=[]
 for number,c in enumerate(credits):
  uid=c['asset_uid'];tiles={}
  for method in BAKE_LABELS:
   r=index[uid,method,4];tiles[method]=actual(r['path'],r['sha256'])
  frame=shared_frame(list(tiles.values()))
  FRAMES.append({'figure':'baked','uid':uid,'frame':frame,'rule':'same union frame across source, GT and every generated condition; no per-method crop'})
  if number<2:panels.append(strip([tiles[m] for m in main],[BAKE_LABELS[m] for m in main],f'({chr(97+number)})',frame,cell=340))
  # A complete, balanced 3x3 condition matrix; no blank cell or duplicate crop row.
  methods=list(BAKE_LABELS);parts=[]
  for offset in range(0,9,3):
   chunk=methods[offset:offset+3]
   parts.append(strip([tiles[m] for m in chunk],[BAKE_LABELS[m] for m in chunk],'',frame,cell=360))
  save(stack(parts,gap=12),f'figS_bake_{number+1:02d}')
 save(stack(panels), 'fig8_baked_unseen_context')

def mva_panel():
 exp=Path('/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010')
 freeze=json.loads((exp/'MVA_MATRIX_FREEZE.json').read_text());rows=json.loads((exp/'mvadapter_matrix/rows.json').read_text());index={(r['object_uid'],r['condition']):r for r in rows}
 with (FIG/'BAKED_ASSET_CREDITS.csv').open() as f:rights={r['asset_uid']:r for r in csv.DictReader(f)}
 selected=[o for o in freeze['objects'] if o['object_uid'] in rights][:2]
 methods={'target':'Target','native_default_1x':'Native / High','fixed_low_0p75':'Fixed Low','fixed_mean_0p83':'Fixed Mean','budget_early16':'Early-high','budget_middle16':'Middle-high','budget_late16':'Late-high','budget_linear_mean_0p83':'Linear'}
 main=['target','fixed_mean_0p83','budget_middle16','budget_late16'];panels=[];supp=[]
 for number,o in enumerate(selected):
  uid=o['object_uid'];gt=o['gt_images_official_order'][0];tiles={'target':actual(gt['path'],gt['sha256'])}
  for method in list(methods)[1:]:tiles[method]=actual(exp/'mvadapter_matrix/predictions'/method/uid/'view_00.png',index[uid,method]['prediction_png_sha256'][0])
  frame=shared_frame(list(tiles.values()));FRAMES.append({'figure':'mvadapter','uid':uid,'frame':frame,'rule':'same union frame across native target and all generated conditions; original backgrounds retained'})
  panels.append(strip([tiles[m] for m in main],[methods[m] for m in main],f'({chr(97+number)})',frame))
  order=list(methods)
  for offset in (0,4):
   chunk=order[offset:offset+4];supp.append(strip([tiles[m] for m in chunk],[methods[m] for m in chunk],f'({chr(97+number)})' if not offset else '',frame))
 save(stack(panels),'fig9_mvadapter_native');save(stack(supp),'figS9_mvadapter_all')
 (FIG/'MVA_VISUAL_SELECTION.json').write_text(json.dumps({'rule':'first two input-order objects in the delivered verified publication-rights ledger; view 0; illustrative, previously observed outcomes','objects':[o['object_uid'] for o in selected]},indent=2))

def schematic():
 def text(x,y,label,size=21):return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{label}</text>'
 def box(x,y,w,h,label,color):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{color}" stroke="#c6d2dc"/>'+text(x+w/2,y+34,label)
 def arrow(path):return f'<path d="{path}" stroke="#49647b" stroke-width="3" fill="none" marker-end="url(#arrow)"/>'
 parts=[box(25,25,185,96,'Reference','#edf3f9'),text(118,88,'Image condition',17),box(25,187,185,130,'Geometry','#edf3f9'),text(118,253,'Normal / Depth',18),text(118,281,'Mask',18),box(270,196,210,110,'GeoTex-Adapter','#fff1df'),text(375,265,'Geometry residuals',17),box(540,196,165,110,'TCAS','#e2f2ed'),text(622,265,'Scale + cap',18),box(540,25,250,96,'Frozen UNet','#e8f0fb'),text(665,88,'ResNet groups',17),box(850,25,185,96,'Output','#edf3f9'),text(942,88,'Six RGB views',18),arrow('M210,73 H540'),arrow('M210,250 H270'),arrow('M480,250 H540'),arrow('M622,196 V121'),arrow('M790,73 H850'),text(710,170,'Inject',17),text(305,350,'Requested C3',19),'<path d="M140,405 H250 V365 H360 V405 H470" fill="none" stroke="#138576" stroke-width="4"/>',text(195,439,'1.25',18),text(305,439,'2.50',18),text(415,439,'1.25',18),text(710,372,'Early / Middle / Late',18),text(710,407,'0–16 / 17–32 / 33–49',18)]
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="1060" height="460"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#49647b"/></marker></defs><rect width="1060" height="460" fill="white"/><g font-family="DejaVu Sans" fill="#233a50">'+''.join(parts)+'</g></svg>'
 (FIG/'fig1_tcas_control.svg').write_text(svg)
 cairosvg.svg2pdf(bytestring=svg.encode(),write_to=str(FIG/'fig1_tcas_control.pdf'));cairosvg.svg2png(bytestring=svg.encode(),write_to=str(FIG/'fig1_tcas_control.png'))

def refresh_manifests():
 names={'fig4':'fig4_freshc_context_roi','fig5':'fig5_freshc_context_roi','fig6_color_diagnostic':'fig6_color_diagnostic_freshc_context_roi'}
 for filename in ['FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv','FIGURE_ASSET_CREDITS.csv']:
  p=FIG/filename
  with p.open() as f:rows=list(csv.DictReader(f));fields=list(rows[0])
  for r in rows:
   if filename.startswith('FRESH'):
    n=names[r['figure_id']];r['output_sha256']=sha(FIG/(n+'.png'));r['figure_pdf_sha256']=sha(FIG/(n+'.pdf'))
   else:r['figure_png_sha256']=sha(FIG/r['figure_png'])
  with p.open('w') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 (FIG/'REVIEW2_SOURCE_HASHES.json').write_text(json.dumps(PROVENANCE,indent=2)+'\n')
 (FIG/'INTEGRATED_DISPLAY_FRAMES.json').write_text(json.dumps(FRAMES,indent=2)+'\n')

if __name__=='__main__':
 fresh_panels();bake_panels();mva_panel();schematic();refresh_manifests()
