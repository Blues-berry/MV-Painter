"""Export the author-selected editable SVG without changing image pixels or layout."""
from pathlib import Path
import base64
import csv
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET

import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'author_supplied' / 'updated_fig1_original.svg'
EXPECTED_SHA = 'a77b8f5489e7a00a1448849861800cb30a4af5e12422afde86e0d12f9e55efe5'
WIDTH_MM = 183.640513
NS = {'svg': 'http://www.w3.org/2000/svg'}


def images(svg):
    rows = []
    for index, element in enumerate(ET.fromstring(svg).findall('.//svg:image', NS)):
        href = element.get('{http://www.w3.org/1999/xlink}href')
        if not href or not href.startswith('data:image/png;base64,'):
            raise ValueError('Every image must be a self-contained PNG slot.')
        data = base64.b64decode(href.split(',', 1)[1])
        raster = Image.open(io.BytesIO(data))
        rows.append({'slot': index, 'embedded_png_sha256': hashlib.sha256(data).hexdigest(),
                     'width_pixels': raster.width, 'height_pixels': raster.height,
                     'identity': 'Author-supplied illustrative imagery; not cohort evidence'})
    return rows


def main():
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SHA:
        raise ValueError('The author-supplied original SVG has changed.')
    original = raw.decode('utf-8')
    # Visio uses a 12 px root font. Absolute sizes avoid CairoSVG's inherited-em
    # conversion discrepancy; 1em tspans retain their parent font size.
    def absolute_font(match):
        factor = float(match.group(1))
        return match.group(0) if factor == 1 else f'font-size:{12 * factor:g}px'
    svg = re.sub(r'font-size:([0-9.]+)em', absolute_font, original)
    viewbox = ET.fromstring(svg).get('viewBox').split()
    height_mm = WIDTH_MM * float(viewbox[3]) / float(viewbox[2])
    svg = re.sub(r'width="11\.933in" height="6\.66948in"',
                 f'width="{WIDTH_MM}mm" height="{height_mm:.8f}mm"', svg, count=1)
    assert images(svg) == images(original), 'Embedded PNG bytes must remain unchanged.'
    (ROOT / 'fig1_tcas_editable.svg').write_text(svg)
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(ROOT / 'fig1_tcas.pdf'))
    for name, width in [('fig1_tcas_preview.png', 1800),
                        ('fig1_tcas_actual_size.png', round(WIDTH_MM / 25.4 * 150)),
                        ('fig1_tcas_half_size.png', round(WIDTH_MM / 25.4 * 75))]:
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(ROOT / name),
                        output_width=width, background_color='white')
    rows = images(svg)
    with (ROOT / 'FIG1_SOURCE_INDEX_FINAL.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    tree = ET.fromstring(svg)
    report = {'original_svg_sha256': EXPECTED_SHA, 'width_mm': WIDTH_MM,
              'height_mm': height_mm, 'editable_texts': len(tree.findall('.//svg:text', NS)),
              'editable_paths': len(tree.findall('.//svg:path', NS)),
              'image_slots': len(rows), 'embedded_pixels_unchanged': True,
              'changes': ['Absolute font sizes for faithful Visio export', 'Publication dimensions'],
              'scope': 'Illustrative interface schematic supplied and approved by author; no experimental UID attribution.',
              'author_approval': 'Design selected by user; final manuscript approval pending.'}
    (ROOT / 'AUTHOR_SVG_EXPORT_CHECK.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Exported author-selected Figure 1; all embedded PNG bytes preserved.')


if __name__ == '__main__':
    main()
