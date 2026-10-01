"""Arrange selected raster stickers without altering artwork. Python + Pillow + reportlab."""
import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

PAPERS = {'A4': (210, 297), 'A5': (148, 210), 'Letter': (215.9, 279.4)}
DENSITY = {'light': (65, 40), 'normal': (80, 50), 'detailed': (95, 65)}
FACTORS = {'small': .75, 'medium': 1, 'large': 1.25}

def positive(value, name, zero=False):
    if isinstance(value, bool):
        raise ValueError(f'{name} must be numeric')
    value = float(value)
    if not math.isfinite(value) or value < 0 or (value == 0 and not zero):
        raise ValueError(f'{name} must be finite and {">=0" if zero else ">0"}')
    return value

def prepare(config, base):
    paper = config.get('paper', 'A4')
    if paper not in PAPERS:
        raise ValueError('paper must be A4, A5 or Letter')
    pw, ph = PAPERS[paper]
    margin = positive(config.get('margin_mm', 10), 'margin_mm')
    gap = positive(config.get('gap_mm', 5), 'gap_mm', zero=True)
    min_ppi = positive(config.get('min_ppi', 300), 'min_ppi')
    # Reserve footer for actual-size calibration and page number.
    aw, ah = pw - 2 * margin, ph - 2 * margin - 8
    if min(aw, ah) <= 0:
        raise ValueError('Margins leave no usable paper')
    items = config.get('items', [])
    if not items:
        raise ValueError('items must contain selected artwork')
    copies_to_pack, warnings, ids = [], [], set()
    for i, item in enumerate(items):
        ident = str(item.get('id', f'sticker-{i+1}'))
        if ident in ids:
            raise ValueError(f'Duplicate id: {ident}')
        ids.add(ident)
        path = (base / item['path']).resolve()
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source)
            image.load()
            pxw, pxh = image.size
            if 'A' in image.getbands() and image.getchannel('A').getbbox() is None:
                raise ValueError(f'{ident}: artwork is fully transparent')
        density = item.get('density', 'normal')
        if density not in DENSITY:
            raise ValueError(f'{ident}: unknown density')
        default_base, default_min = DENSITY[density]
        nominal = positive(item.get('base_long_edge_mm', default_base), 'base_long_edge_mm')
        minimum = positive(item.get('min_long_edge_mm', default_min), 'min_long_edge_mm')
        copies = item.get('copies', 1)
        if isinstance(copies, bool) or not isinstance(copies, int) or copies < 1:
            raise ValueError(f'{ident}: copies must be a positive integer')
        sizes = item.get('sizes', ['small', 'medium', 'large'])
        if not isinstance(sizes, list) or not sizes or len(set(sizes)) != len(sizes):
            raise ValueError(f'{ident}: sizes must be a nonempty unique list')
        ratio_w, ratio_h = pxw / max(pxw, pxh), pxh / max(pxw, pxh)
        cap = min(max(pxw, pxh) / min_ppi * 25.4, aw / ratio_w, ah / ratio_h)
        if cap + 1e-6 < minimum:
            raise ValueError(f'{ident}: resolution/paper permits {cap:.1f}mm, below readable minimum {minimum:.1f}mm')
        variants = {}
        for size in sizes:
            if size not in FACTORS:
                raise ValueError(f'{ident}: unknown size {size}')
            desired = nominal * FACTORS[size]
            # Round down so rounding never drops PPI below requested minimum.
            long_edge = math.floor(max(minimum, min(desired, cap)) * 100) / 100
            if abs(long_edge - desired) > .02:
                warnings.append(f'{ident}/{size}: {desired:.1f}mm adjusted to {long_edge:.2f}mm for readability, pixels or paper')
            v = variants.setdefault(long_edge, {'labels': [], 'copies': 0})
            v['labels'].append(size)
            v['copies'] += copies
        for edge, v in variants.items():
            if len(v['labels']) > 1:
                warnings.append(f'{ident}: {"/".join(v["labels"])} share {edge:.2f}mm; copies combined')
            w, h = edge * ratio_w, edge * ratio_h
            for copy in range(v['copies']):
                copies_to_pack.append({'id': ident, 'path': str(path), 'sizes': v['labels'],
                    'copy': copy + 1, 'width_mm': w, 'height_mm': h,
                    'ppi': min(pxw / (w / 25.4), pxh / (h / 25.4)), 'pixels': [pxw, pxh]})
    return (pw, ph, margin, gap, aw, ah), copies_to_pack, warnings

def pack(geometry, items):
    pw, ph, margin, gap, aw, ah = geometry
    pages = []
    # Shelf packing across existing pages, largest/tallest first. No forced rotations.
    for item in sorted(items, key=lambda x: (-x['height_mm'], -x['width_mm'])):
        w, h = item['width_mm'], item['height_mm']
        placed = False
        for page in pages:
            for shelf in page['shelves']:
                if h <= shelf['height'] + 1e-6 and shelf['x'] + w <= aw + 1e-6:
                    item.update(x_mm=margin+shelf['x'], y_top_mm=margin+shelf['y'])
                    shelf['x'] += w + gap
                    page['items'].append(item); placed = True; break
            if placed: break
            next_y = page['used'] + gap
            if next_y + h <= ah + 1e-6:
                page['shelves'].append({'y': next_y, 'x': w+gap, 'height': h})
                page['used'] = next_y+h
                item.update(x_mm=margin, y_top_mm=margin+next_y)
                page['items'].append(item); placed = True; break
        if not placed:
            item.update(x_mm=margin, y_top_mm=margin)
            pages.append({'shelves': [{'y': 0, 'x': w+gap, 'height': h}], 'used': h, 'items': [item]})
    for n, page in enumerate(pages, 1):
        for item in page['items']: item['page'] = n
    return pages

def create_sheet(manifest, output):
    manifest, output = Path(manifest).resolve(), Path(output).resolve()
    config = json.loads(manifest.read_text(encoding='utf-8-sig'))
    geometry, items, warnings = prepare(config, manifest.parent)
    pages = pack(geometry, items)
    pw, ph, margin, gap, _, _ = geometry
    guides = config.get('guides', False)
    if not isinstance(guides, bool): raise ValueError('guides must be true or false')
    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=(pw*mm, ph*mm))
    c.setTitle('Travel stickers - actual size print sheet')
    for index, page in enumerate(pages, 1):
        for item in page['items']:
            x, y = item['x_mm']*mm, (ph-item['y_top_mm']-item['height_mm'])*mm
            with Image.open(item['path']) as source:
                im = ImageOps.exif_transpose(source).convert('RGBA')
                c.drawImage(ImageReader(im), x, y, width=item['width_mm']*mm,
                            height=item['height_mm']*mm, mask='auto')
            if guides:
                c.saveState(); c.setStrokeColorRGB(.7,.7,.7); c.setLineWidth(.3); c.setDash(2,2)
                c.rect(x,y,item['width_mm']*mm,item['height_mm']*mm); c.restoreState()
        c.setFont('Helvetica', 8); c.setFillColorRGB(.3,.3,.3)
        c.drawString(margin*mm, 5*mm, f'Print at 100% / Actual size   |   {index}/{len(pages)}')
        c.setStrokeColorRGB(.3,.3,.3); c.setLineWidth(.5)
        x=(pw-margin-20)*mm; y=6*mm
        c.line(x,y,x+20*mm,y); c.line(x,y-mm,x,y+mm); c.line(x+20*mm,y-mm,x+20*mm,y+mm)
        c.drawRightString(x-2*mm,5*mm,'20 mm')
        c.showPage()
    c.save()
    result={'paper_mm':[pw,ph], 'margin_mm':margin,'gap_mm':gap,'page_count':len(pages),
            'item_count':len(items),'warnings':warnings,'guides':'rectangle only' if guides else 'none',
            'dimensions':'source canvas; preserves transparent padding',
            'placements':[i for page in pages for i in page['items']]}
    output.with_suffix('.layout.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest'); parser.add_argument('--output',required=True)
    args=parser.parse_args()
    try:
        result=create_sheet(args.manifest,args.output)
    except (ValueError,KeyError,OSError,TypeError) as exc:
        parser.exit(2,f'Layout failed: {exc}\n')
    print(json.dumps({'pages':result['page_count'],'copies':result['item_count'],'warnings':result['warnings']},ensure_ascii=False))
