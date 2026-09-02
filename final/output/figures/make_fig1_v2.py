"""fig1 rebuild v2 — color-keyed surgery on the original submission's Fig.1.
Purple = FAC elements (unique color) -> white. Teal arrow+TCAS band -> moved up
as one piece. Run from final/figures."""
from PIL import Image
import subprocess, numpy as np

SRC = "/4T/CXY/MV-Painter/anonymous_submission_0709_final.pdf"
OUT = "/4T/CXY/MV-Painter/final/figures"
TMP = "/tmp/fig1_src2"
subprocess.run(["pdftoppm", "-png", "-r", "200", "-f", "4", "-l", "4", SRC, TMP], check=True)
page = Image.open(f"{TMP}-04.png").convert("RGB")
W, H = page.size
fig = page.crop((int(.045*W), int(.068*H), int(.99*W), int(.50*H)))
a = np.array(fig).astype(int)
FW, FH = fig.size
R, G, B = a[..., 0], a[..., 1], a[..., 2]

purple = (R > 80) & (R < 200) & (B > 120) & (B < 240) & (R - G > 40) & (B - G > 40)
print("purple px:", purple.sum())
a[purple] = [255, 255, 255]                      # kill all FAC traces

teal = (G > 70) & (G < 180) & (B > 70) & (B < 180) & (G - R > 30) & (B - R > 30)
cols = teal.sum(axis=0)
xs = np.where(cols > 8)[0]
# TCAS assembly: teal pixels below y=0.62*FH (box + arrow), x-range from them
ys = np.where(teal[int(.60*FH):, :].sum(axis=1) > 8)[0] + int(.60*FH)
x0, x1 = int(xs.min()) - 8, int(xs.max()) + 8
y0, y1 = int(ys.min()) - 6, int(ys.max()) + 8    # arrow top .. TCAS bottom
print("teal assembly bbox:", x0, y0, x1, y1)
assembly = a[y0:y1, x0:x1].copy()

# find UNet box bottom: long horizontal blue border above the assembly zone
blue = (B - R > 40) & (B - G > 20) & (B > 120)
rows = blue[: int(.60*FH), :].sum(axis=1)
unet_bottom = max(np.where(rows > FW * 0.35)[0])
print("unet_bottom:", unet_bottom)

a[y0:y1, x0:x1] = [255, 255, 255]                # clear old location
dst_y = unet_bottom + 18                          # paste right below UNet box
a[dst_y:dst_y + (y1 - y0), x0:x1] = assembly
a[int(dst_y + (y1 - y0)) + 2:, :] = [255, 255, 255]  # trim everything below
out = Image.fromarray(a.astype(np.uint8))
out.save(f"{OUT}/fig1.png")
subprocess.run(["gs", "-dBATCH", "-dNOPAUSE", "-sDEVICE=pdfwrite", "-o",
                f"{OUT}/fig1.pdf", f"{OUT}/fig1.png"], check=True,
               stdout=subprocess.DEVNULL)
print("done", out.size)
