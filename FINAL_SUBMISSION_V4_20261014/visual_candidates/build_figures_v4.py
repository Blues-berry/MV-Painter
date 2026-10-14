"""Render current V4 figures from verified selected pixels and frozen selection records."""
from pathlib import Path
import argparse,hashlib,json
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1]
pdfmetrics.registerFont(TTFont('V4Sans','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
def text(c,x,y,s,size=8):
 c.setFont('V4Sans',size);c.setFillColorRGB(.10,.15,.22);c.drawString(x,y,s)
def image(c,p,box):
 path=ROOT/p['display_asset'];assert hashlib.sha256(path.read_bytes()).hexdigest()==p['display_sha256']
 x,y,w,h=box;c.setStrokeColorRGB(.78,.81,.85);c.setLineWidth(.4);c.rect(x,y,w,h)
 c.drawImage(ImageReader(str(path)),x+3,y+3,w-6,h-6,preserveAspectRatio=True,anchor='c',mask='auto')
def figure3(config,out):
 rows=config['rows'];height=178 if len(rows)==1 else 328;c=canvas.Canvas(str(out),pagesize=(576,height));c.setTitle('Figure 3 — reference mismatch and allocation effects')
 labels=['GT-256 self-bake','Fixed Mean','Late-high'];margin,gap=12,10;cw=(576-2*margin-2*gap)/3
 for j,l in enumerate(labels):text(c,margin+j*(cw+gap)+3,height-14,l,8.6)
 for i,row in enumerate(rows):
  top=height-37-i*150
  title='Stone' if row['title']=='หิน' else ('Tire' if 'Tire'==row['title'] else 'Baptismal font')
  text(c,12,top,row['role']+' | '+title+' | '+row['uid'][:12],8)
  for j,p in enumerate(row['panels']):image(c,p,(margin+j*(cw+gap),top-126,cw,118))
  text(c,12,top-139,f"11-view Late - Mean: FG-LPIPS {row['delta_lpips']:+.6f}; FG-PSNR {row['delta_psnr_db']:+.3f} dB",7.4)
 c.save()
def figure2(config,out):
 rows=config['rows'];height=390;c=canvas.Canvas(str(out),pagesize=(576,height));c.setTitle('Figure 2 — complete competitive controls, raw view 000')
 margin,gap=8,5;cw=(576-2*margin-4*gap)/5
 for j,p in enumerate(rows[0]['panels']):text(c,margin+j*(cw+gap)+2,height-15,p['label'],8.5)
 for i,row in enumerate(rows):
  y=height-33-i*117
  title={'Color-rich texture':'Input-property example | Green Iguan','Positive endpoint example':'Post-outcome positive example | Mosque','Adverse endpoint example':'Post-outcome adverse example | Specimen 103'}[row['role']]
  text(c,8,y,title+' | '+row['uid'][:12],7.7)
  for j,p in enumerate(row['panels']):image(c,p,(margin+j*(cw+gap),y-104,cw,100))
 text(c,8,5,'Full raw-view-000 frames; all five conditions retained. Selected illustrations do not estimate prevalence.',6.9)
 c.save()
def main():
 p=argparse.ArgumentParser();p.add_argument('--figure3-selection',type=Path,default=ROOT/'quality_review/FIGURE3_B_SELECTION_V4.json');p.add_argument('--figure3-output',type=Path,default=ROOT/'figures/fig3_bake10_two_object_v4.pdf');p.add_argument('--skip-figure2',action='store_true');a=p.parse_args()
 figure3(json.loads(a.figure3_selection.read_text()),a.figure3_output)
 if not a.skip_figure2:figure2(json.loads((ROOT/'visual_candidates/FIGURE2_SELECTION_V4.json').read_text()),ROOT/'figures/fig2_freshc_controls_v4.pdf')
if __name__=='__main__':main()
