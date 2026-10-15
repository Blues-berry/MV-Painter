"""Rebuild archived Figure 3 candidate C for review; never used by the main manuscript."""
from pathlib import Path
import argparse
import hashlib, json
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / 'quality_review/FIGURE3_C_REVIEW_ONLY_V4.pdf'
ROW = json.loads((ROOT/'quality_review/FIGURE3_C_SELECTION_ARCHIVE_V4.json').read_text())['rows'][0]
# Transcribed without recalculation from S5's frozen ten-object table, in source UID order.
EFFECTS = [
 ('LG remote',-.00408), ('Tire',-.00279), ('Stone',-.00046),
 ('Font',-.00781), ('Bridge',-.00003), ('News boxes',-.00318),
 ('Turtle shell',-.00445), ('e261c0',-.00168), ('f1ccc5',-.00137),
 ('fa5c4b',-.00065),
]

def verified(panel):
    path=ROOT/panel['display_asset']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==panel['display_sha256']
    return ImageReader(str(path))

def label(c,x,y,s,size=7.5):
    c.setFont('V4Sans',size);c.setFillColorRGB(.11,.16,.22);c.drawString(x,y,s)

def box(c,im,x,y,w,h):
    c.setStrokeColorRGB(.77,.80,.84);c.setLineWidth(.4);c.rect(x,y,w,h)
    c.drawImage(im,x+3,y+3,w-6,h-6,preserveAspectRatio=True,anchor='c',mask='auto')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=DEFAULT_OUT)
    out=parser.parse_args().output
    pdfmetrics.registerFont(TTFont('V4Sans','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    c=canvas.Canvas(str(out),pagesize=(576,340))
    c.setTitle('GeoTex Bake10: matched appearance and ten-object effects')
    label(c,12,323,'Input reference',8)
    label(c,12,311,'raw000; different camera',6.8)
    for x,s in [(114,'GT-256 self-bake'),(267,'Fixed Mean'),(420,'Late-high')]:label(c,x,323,s,8)
    inp=ROOT/ROW['input_asset']
    assert hashlib.sha256(inp.read_bytes()).hexdigest()==ROW['input_sha256']
    box(c,ImageReader(str(inp)),12,186,90,115)
    for j,p in enumerate(ROW['panels']):box(c,verified(p),114+j*153,186,143,115)
    label(c,114,174,'Tire: input-property median of seven cleared assets; unseen camera 004',7.3)
    label(c,114,164,'11-view Late - Mean: FG-LPIPS -0.002791; FG-PSNR +0.257 dB',7.0)
    label(c,12,148,'All ten Bake10 objects: Late-high - Fixed Mean FG-LPIPS (11 unseen views each)',8)
    label(c,12,137,'Compatibility-selected pilot; negative values favor Late-high; no object removed.',6.8)
    x0,x1=95,558;minv,maxv=-.008,0
    def xpos(v):return x0+(v-minv)/(maxv-minv)*(x1-x0)
    for t in [-.008,-.006,-.004,-.002,0]:
        x=xpos(t);c.setStrokeColorRGB(.86,.88,.9);c.line(x,19,x,126);label(c,x-11,7,f'{t:.3f}',6.2)
    c.setStrokeColorRGB(.23,.32,.42);c.line(xpos(0),19,xpos(0),126)
    for i,(name,v) in enumerate(EFFECTS):
        y=120-i*10.6;label(c,12,y-2,name,6.6)
        c.setFillColorRGB(.14,.36,.57) if name=='Tire' else c.setFillColorRGB(.40,.48,.56)
        c.circle(xpos(v),y,2.6,fill=1,stroke=0)
    c.save()
    print(out)

if __name__=='__main__':main()
