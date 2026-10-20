#!/usr/bin/env python3
"""Ingest tool (run by Claude/owner locally, needs Pillow).
Converts source infographics to web images under _src/img/<id>/ and adds/updates the piece in data/pieces.json.
Library use: add_piece(meta, en_imgs, fa_imgs). CLI for a standard EN/FA folder:
  python3 ingest.py folder <dir-with-EN-and-FA> --id ID --series pahlavi --date YYYY-MM-DD --topics a,b --title-en .. --title-fa ..
"""
import json, os, re, sys, glob, shutil, argparse
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data', 'pieces.json')
IMG = os.path.join(HERE, 'img')

def load():
    return json.load(open(DATA, encoding='utf8')) if os.path.exists(DATA) else []
def save(items):
    items.sort(key=lambda p: (p['date'], p['id']))
    json.dump(items, open(DATA, 'w', encoding='utf8'), ensure_ascii=False, indent=1)

def make_images(src, outdir, stem):
    """src image -> stem.webp (1800w), stem-t.webp (640w), stem-og.jpg (1200x675), stem-x.jpg (<=4096w download)"""
    os.makedirs(outdir, exist_ok=True)
    im = Image.open(src).convert('RGB')
    def rs(w):
        h = round(im.height * w / im.width)
        return im.resize((w, h), Image.LANCZOS) if im.width > w else im.copy()
    rs(1800).save(f'{outdir}/{stem}.webp', 'WEBP', quality=84, method=6)
    rs(640).save(f'{outdir}/{stem}-t.webp', 'WEBP', quality=80, method=6)
    og = rs(1200); og.save(f'{outdir}/{stem}-og.jpg', 'JPEG', quality=86, optimize=True)
    if src.lower().endswith(('.jpg', '.jpeg')) and im.width <= 4096:
        shutil.copy(src, f'{outdir}/{stem}-x.jpg')
    else:
        rs(4096).save(f'{outdir}/{stem}-x.jpg', 'JPEG', quality=90, optimize=True)
    return {'w': im.width, 'h': im.height}

def add_piece(meta, en_imgs, fa_imgs):
    # Site policy (19 Oct 2026): no politically sensitive infographics about current events. Historical political pieces are fine.
    if meta.get('current_politics'): raise SystemExit('Blocked by site policy: current-events political content is not published on the website')
    pid = meta['id']; out = os.path.join(IMG, pid)
    if os.path.isdir(out): shutil.rmtree(out)
    meta['images'] = {'en': [], 'fa': []}
    for lang, lst in (('en', en_imgs), ('fa', fa_imgs)):
        for i, p in enumerate(lst, 1):
            stem = f'{lang}-{i}'
            make_images(p, out, stem)
            meta['images'][lang].append(stem)
    items = [x for x in load() if x['id'] != pid]
    items.append(meta); save(items)

# ---------- markdown parsing ----------
def sections(text):
    parts = re.split(r'^## ', text, flags=re.M)
    out = []
    for p in parts[1:]:
        h, _, b = p.partition('\n')
        out.append((h.strip(), b.strip()))
    return out
def clean(s):
    s = re.sub(r'^\*[^*\n]*\*\s*$', '', s, flags=re.M)         # italic meta lines
    s = re.sub(r'^---+\s*$', '', s, flags=re.M)
    return re.sub(r'\n{3,}', '\n\n', s).strip()
def numbered(body):
    items = re.split(r'^\s*\d+\.\s+', body, flags=re.M)
    return [clean(x) for x in items[1:] if clean(x)]
def parse_posts_md(path):
    """Handles the W2 format (## Posts / ### n. label / ## Alt text) and W3/Special format (## Caption / ## ALT text / ## Text-only posts)."""
    r = {'caption': '', 'alt': '', 'posts': []}
    if not path or not os.path.exists(path): return r
    t = open(path, encoding='utf8').read()
    for h, b in sections(t):
        hl = h.lower()
        if hl.startswith('caption') or h.startswith('کپشن'):
            r['caption'] = clean(b)
        elif hl.startswith('alt') or 'جایگزین' in h:
            r['alt'] = clean(b)
        elif 'text-only' in hl or 'متنی' in h:
            r['posts'] = numbered(b)
        elif hl.startswith('posts') or h.startswith('پست‌ها'):
            blocks = re.split(r'^### ', b, flags=re.M)[1:]
            texts = []
            for blk in blocks:
                head, _, body = blk.partition('\n')
                if re.search(r'Image: Photo|تصویر: عکس', body): continue
                body = clean(body)
                if '[Photo' in body or '[منبع' in body: continue
                texts.append(body)
            if texts:
                r['caption'] = texts[0]; r['posts'] = texts[1:]
    r['alt'] = re.sub(r'\s*\(\d+ characters\)$', '', r['alt'])
    return r
def parse_w1(path):
    r = {'en': {'caption': '', 'alt': '', 'posts': []}, 'fa': {'caption': '', 'alt': '', 'posts': []}}
    t = open(path, encoding='utf8').read()
    for h, b in sections(t):
        if h.startswith('Post 1'): r['en']['caption'] = clean(b)
        elif h.startswith('Post 2'): r['fa']['caption'] = clean(b)
        elif h.startswith('Post 3') or h.startswith('Post 4'):
            b = clean(b)
            if not b.lower().startswith('source note'): r['en']['posts'].append(b)
    return r

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('mode'); ap.add_argument('dir')
    ap.add_argument('--id', required=True); ap.add_argument('--series', required=True); ap.add_argument('--date', required=True)
    ap.add_argument('--topics', default=''); ap.add_argument('--title-en', required=True); ap.add_argument('--title-fa', required=True)
    a = ap.parse_args()
    en = sorted(glob.glob(f'{a.dir}/EN/*branded_X4096.jpg')); fa = sorted(glob.glob(f'{a.dir}/FA/*branded_X4096.jpg'))
    pe = parse_posts_md(os.path.join(a.dir, 'EN', 'Posts_EN.md')); pf = parse_posts_md(os.path.join(a.dir, 'FA', 'Posts_FA.md'))
    meta = {'id': a.id, 'series': a.series, 'date': a.date, 'topics': [x for x in a.topics.split(',') if x],
            'title': {'en': a.title_en, 'fa': a.title_fa}, 'caption': {'en': pe['caption'], 'fa': pf['caption']},
            'alt': {'en': pe['alt'], 'fa': pf['alt']}, 'posts': {'en': pe['posts'], 'fa': pf['posts']}}
    add_piece(meta, en, fa); print('added', a.id)
