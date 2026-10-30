#!/usr/bin/env python3
"""Airyanem Atlas static site generator (stdlib only).

  python3 _src/build.py [--today YYYY-MM-DD] [--out _site]

Reads _src/data/{pieces,evening,config}.json and _src/img/, writes the site to --out.
Only items with date <= today are published (publish-date gating). Run daily by .github/workflows/site.yml.
"""
import json, os, re, sys, shutil, html, argparse, datetime
from xml.sax.saxutils import escape as xesc

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D = lambda *p: os.path.join(HERE, *p)

# ------------------------------------------------------------------ i18n
S = {
 'en': {
  'dir': 'ltr', 'name': 'Airyanem Atlas',
  'tag': 'Indo-European & Iranian history, language and maps. Sources on every graphic.',
  'home': 'Home', 'archive': 'Archive', 'specials': 'Daily Specials', 'evening': 'Evening Posts', 'notes': 'Notes', 'pahlavi': 'Pahlavi Era', 'about': 'About',
  'latest': 'Latest', 'all': 'All', 'series': 'Series', 'topic': 'Topic', 'search': 'Search the archive', 'results': 'infographics',
  'view': 'View infographic', 'download': 'Download high-res JPG', 'copy': 'Copy caption', 'copyt': 'Copy text', 'copied': 'Copied', 'share': 'Share on X',
  'alt': 'Image description', 'takes': 'Short takes', 'caption': 'Caption', 'infolang': 'Infographic language',
  'prev': 'Previous', 'next': 'Next', 'more': 'More in this series', 'on_x': 'Follow on X', 'follow': 'Follow',
  'hero_kicker': 'Latest infographic', 'hero_sub': 'From the steppe to Persepolis',
  'sec_specials': 'Daily Special', 'sec_specials_d': 'A new infographic built from what happened on this day in history, or from the news.',
  'sec_evening': 'Evening Posts', 'sec_evening_d': 'A deep fact and a fun fact, every evening.',
  'sec_notes_d': 'Short history notes with photos, grouped by theme.', 'photo': 'Photo', 'on_x_post': 'Photos as posted on X',
  'sec_pahlavi': 'Pahlavi Era', 'sec_pahlavi_d': 'A dedicated collection on the Pahlavi era, updated regularly.',
  'sec_topics': 'Browse by topic', 'see_all': 'See all', 'coming': 'The Pahlavi Era collection is being prepared. New infographics will appear here.',
  'empty': 'Nothing here yet.', 'fact_a': 'Deep fact', 'fact_b': 'Fun fact', 'source': 'Source', 'by': 'by',
 'course': 'Course', 'course_h': 'Indo-European Course', 'course_d': 'Five illustrated slide modules on the origins of the Indo-European languages, ancient DNA, archaeology, the comparative method and the Indo-Iranians. Read online, free.',
  'mod': 'Module', 'slides': 'slides', 'open_mod': 'Open module', 'read_on': 'Read online', 'dl_pdf': 'Download PDF', 'pptx_pat': 'Editable PowerPoint on Patreon', 'contents': 'All slides', 'parts_h': 'Parts', 'prev_s': 'Previous', 'next_s': 'Next', 'fullscr': 'Full screen', 'all_mods': 'All modules',
  'course_who': ['Built as study and reference material for history students and enthusiasts.', 'Every slide carries its sources; evidence is graded A (checked in a supplied paper), B (standard background) or C (interpretation or debate).', 'Use the arrow keys, swipe, or click the right and left side of a slide to move through it.'],
  'course_note_h': 'Good to know', 'course_note': 'The slides are written in English. Editable PowerPoint versions are available to Patreon supporters.',
  'about_title': 'About Airyanem Atlas', 'contact': 'Contact', 'rss': 'RSS feed', 'rights': 'All rights reserved.',
  'lang_switch': 'فارسی', 'lang_switch_title': 'Switch to Farsi', 'skip': 'Skip to content', 'menu': 'Menu',
  'about_p': ['Airyanem Atlas is a visual atlas of Indo-European and Iranian history, language and maps: one infographic a day, from the steppe to Persepolis and beyond.',
              'Every graphic carries its sources, and every piece is published in English and Farsi.',
              'The project is created and edited by Cassian Ysatis, the pen name of the writer behind the account.'],
  'about_h2': ['What you will find here', 'Follow along'],
  'about_list': ['Infographics on language families, empires, archaeology, texts and heritage, in English and Farsi.',
                 'Daily Specials: a new infographic tied to the day in history or the news.',
                 'Evening Posts: a deep fact and a fun fact every evening.',
                 'The Pahlavi Era collection, updated regularly.'],
 },
 'fa': {
  'dir': 'rtl', 'name': 'اطلس آیریانم',
  'tag': 'تاریخ، زبان و نقشهٔ هندواروپایی و ایرانی. منبع روی هر گرافیک.',
  'home': 'خانه', 'archive': 'بایگانی', 'specials': 'ویژهٔ روز', 'evening': 'پست‌های شامگاهی', 'notes': 'یادداشت‌ها', 'pahlavi': 'دورهٔ پهلوی', 'about': 'دربارهٔ ما',
  'latest': 'تازه‌ترین‌ها', 'all': 'همه', 'series': 'مجموعه', 'topic': 'موضوع', 'search': 'جستجو در بایگانی', 'results': 'اینفوگرافیک',
  'view': 'دیدن اینفوگرافیک', 'download': 'دریافت JPG با کیفیت بالا', 'copy': 'رونوشت کپشن', 'copyt': 'رونوشت متن', 'copied': 'رونوشت شد', 'share': 'اشتراک در ایکس',
  'alt': 'توضیح تصویر', 'takes': 'نکته‌های کوتاه', 'caption': 'کپشن', 'infolang': 'زبان اینفوگرافیک',
  'prev': 'قبلی', 'next': 'بعدی', 'more': 'بیشتر از این مجموعه', 'on_x': 'دنبال‌کردن در ایکس', 'follow': 'دنبال کنید',
  'hero_kicker': 'تازه‌ترین اینفوگرافیک', 'hero_sub': 'از استپ تا تخت جمشید',
  'sec_specials': 'ویژهٔ روز', 'sec_specials_d': 'اینفوگرافیکی تازه، برگرفته از رویدادهای چنین روزی در تاریخ یا از اخبار روز.',
  'sec_evening': 'پست‌های شامگاهی', 'sec_evening_d': 'هر شب یک نکتهٔ ژرف و یک نکتهٔ جالب.',
  'sec_notes_d': 'یادداشت‌های کوتاه تاریخی همراه با عکس، دسته‌بندی‌شده بر پایهٔ موضوع.', 'photo': 'عکس', 'on_x_post': 'عکس‌ها مطابق پست ایکس',
  'sec_pahlavi': 'دورهٔ پهلوی', 'sec_pahlavi_d': 'مجموعه‌ای ویژه دربارهٔ دورهٔ پهلوی که پیوسته به‌روز می‌شود.',
  'sec_topics': 'گشت‌وگذار بر پایهٔ موضوع', 'see_all': 'دیدن همه', 'coming': 'مجموعهٔ دورهٔ پهلوی در دست آماده‌سازی است. اینفوگرافیک‌های تازه همین‌جا خواهند آمد.',
  'empty': 'هنوز چیزی اینجا نیست.', 'fact_a': 'نکتهٔ ژرف', 'fact_b': 'نکتهٔ جالب', 'source': 'منبع', 'by': 'از',
 'course': 'دوره', 'course_h': 'دورهٔ هندواروپایی', 'course_d': 'پنج بخش اسلایدی مصور دربارهٔ خاستگاه زبان‌های هندواروپایی، دی‌ان‌ای باستانی، باستان‌شناسی، روش تطبیقی و هندوایرانیان. رایگان و آنلاین.',
  'mod': 'بخش', 'slides': 'اسلاید', 'open_mod': 'باز کردن بخش', 'read_on': 'خواندن آنلاین', 'dl_pdf': 'دریافت PDF', 'pptx_pat': 'پاورپوینت ویرایش‌پذیر در پاترئون', 'contents': 'همهٔ اسلایدها', 'parts_h': 'بخش‌ها', 'prev_s': 'قبلی', 'next_s': 'بعدی', 'fullscr': 'تمام‌صفحه', 'all_mods': 'همهٔ بخش‌ها',
  'course_who': ['ساخته‌شده به‌عنوان مواد آموزشی و مرجع برای دانشجویان و دوستداران تاریخ.', 'روی هر اسلاید منبعش آمده است و شواهد درجه‌بندی شده‌اند: A (بررسی‌شده در مقالهٔ در دسترس)، B (پیشینهٔ استاندارد) یا C (تفسیر یا محل بحث).', 'محتوای اسلایدها انگلیسی است؛ فهرست و راهنما در این صفحه فارسی است.'],
  'course_note_h': 'نکته', 'course_note': 'اسلایدها به زبان انگلیسی نوشته شده‌اند. نسخهٔ پاورپوینت ویرایش‌پذیر برای حامیان پاترئون در دسترس است.',
  'about_title': 'دربارهٔ اطلس آیریانم', 'contact': 'تماس', 'rss': 'خوراک آر‌اس‌اس', 'rights': 'همهٔ حقوق محفوظ است.',
  'lang_switch': 'English', 'lang_switch_title': 'Switch to English', 'skip': 'پرش به محتوا', 'menu': 'فهرست',
  'about_p': ['اطلس آیریانم اطلسی تصویری از تاریخ، زبان و نقشهٔ هندواروپایی و ایرانی است: هر روز یک اینفوگرافیک، از استپ تا تخت جمشید و فراتر.',
              'روی هر گرافیک منبعش آمده است و هر اثر به دو زبان انگلیسی و فارسی منتشر می‌شود.',
              'این پروژه را کاسیان ایساتیس می‌سازد و ویرایش می‌کند؛ نام قلمی نویسندهٔ پشت این حساب.'],
  'about_h2': ['اینجا چه می‌یابید', 'ما را دنبال کنید'],
  'about_list': ['اینفوگرافیک دربارهٔ خانواده‌های زبانی، امپراتوری‌ها، باستان‌شناسی، متن‌ها و میراث، به انگلیسی و فارسی.',
                 'ویژهٔ روز: اینفوگرافیکی تازه، وابسته به رویدادهای چنین روزی در تاریخ یا اخبار.',
                 'پست‌های شامگاهی: هر شب یک نکتهٔ ژرف و یک نکتهٔ جالب.',
                 'مجموعهٔ دورهٔ پهلوی که پیوسته به‌روز می‌شود.'],
 },
}
SERIES = {  # id: (en, fa)
 'special': ('Daily Special', 'ویژهٔ روز'), 'pahlavi': ('Pahlavi Era', 'دورهٔ پهلوی'),
 'w5': ('Week 5', 'هفتهٔ ۵'), 'w4': ('Week 4', 'هفتهٔ ۴'), 'w3': ('Week 3', 'هفتهٔ ۳'), 'w2': ('Week 2', 'هفتهٔ ۲'), 'w1': ('Week 1', 'هفتهٔ ۱'), 'launch': ('Launch', 'آغاز'),
}
NOTE_TOPICS = {'achaemenid': ('Achaemenid Persia', 'ایران هخامنشی'), 'science': ('Water, science and technology', 'آب، دانش و فناوری'), 'hittites': ('Hittites and Indo-European links', 'هیتی‌ها و پیوندهای هندواروپایی'), 'neighbours': ('Ancient neighbours of Persia', 'همسایگان باستانی ایران')}
TOPICS = {
 'language': ('Language', 'زبان'), 'empire': ('Empires & Kings', 'امپراتوری‌ها و شاهان'), 'archaeology': ('Archaeology', 'باستان‌شناسی'),
 'culture': ('Culture & Myth', 'فرهنگ و اسطوره'), 'maps': ('Maps', 'نقشه‌ها'), 'heritage': ('Heritage', 'میراث'),
 'history': ('History', 'تاریخ'), 'news': ('News', 'اخبار'), 'science': ('Science & Technology', 'دانش و فناوری'),
 'economy': ('Economy', 'اقتصاد'), 'society': ('Society', 'جامعه'), 'military': ('Military', 'نیروهای مسلح'), 'politics': ('Politics & Diplomacy', 'سیاست و دیپلماسی'),
}
MONTHS_EN = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
MONTHS_FA = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']

def fa_digits(s): return str(s).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))
def g2j(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = 355666 + 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400 + gd + g_d_m[gm - 1]
    jy = -1595 + 33 * (days // 12053); days %= 12053
    jy += 4 * (days // 1461); days %= 1461
    if days > 365: jy += (days - 1) // 365; days = (days - 1) % 365
    if days < 186: jm = 1 + days // 31; jd = 1 + days % 31
    else: jm = 7 + (days - 186) // 30; jd = 1 + (days - 186) % 30
    return jy, jm, jd
def fdate(iso, lang):
    y, m, d = map(int, iso.split('-'))
    if lang == 'fa':
        jy, jm, jd = g2j(y, m, d); return f'{fa_digits(jd)} {MONTHS_FA[jm-1]} {fa_digits(jy)}'
    return f'{d} {MONTHS_EN[m-1]} {y}'
def rfc822(iso):
    return datetime.datetime.strptime(iso, '%Y-%m-%d').strftime('%a, %d %b %Y 07:00:00 -0700')

E = lambda s: html.escape(str(s), quote=True)
def lede(c, n=240):
    c = re.sub(r'\s+', ' ', re.sub(r'#\S+', '', c)).strip()
    if len(c) <= n: return c
    c = c[:n].rsplit(' ', 1)[0].rstrip(',;:')
    return c + '…'
def para(s):  # plain text -> html with line breaks
    return '<br>'.join(E(x) for x in s.strip().split('\n'))

# ------------------------------------------------------------------ data
def load_json(name, default):
    p = D('data', name)
    return json.load(open(p, encoding='utf8')) if os.path.exists(p) else default

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--today'); ap.add_argument('--out', default=os.path.join(ROOT, '_site'))
    a = ap.parse_args()
    if a.today: today = a.today
    else:
        try:
            from zoneinfo import ZoneInfo
            today = datetime.datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%Y-%m-%d')
        except Exception:
            today = (datetime.datetime.utcnow() - datetime.timedelta(hours=7)).strftime('%Y-%m-%d')
    OUT = a.out
    cfg = load_json('config.json', {})
    SITE = cfg['site_url'].rstrip('/')
    social = cfg.get('social', {})
    pieces = [p for p in load_json('pieces.json', []) if p['date'] <= today]
    pieces.sort(key=lambda p: (p['date'], p['id']), reverse=True)
    evening = [e for e in load_json('evening.json', []) if e['date'] <= today]
    evening.sort(key=lambda e: e['date'], reverse=True)
    notes = [n for n in load_json('notes.json', []) if n['date'] <= today]
    notes.sort(key=lambda n: (n['date'], n['id']), reverse=True)
    byid = {p['id']: p for p in pieces}

    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    # static assets
    shutil.copytree(D('web'), os.path.join(OUT, 'assets'))
    for f in os.listdir(D('assets')): shutil.copy(D('assets', f), os.path.join(OUT, 'assets', f))
    for p in pieces:
        src = D('img', p['id'])
        if os.path.isdir(src): shutil.copytree(src, os.path.join(OUT, 'img', p['id']))
    course = [c for c in load_json('course.json', []) if c['date'] <= today]
    for c in course:
        src = D('course', c['id'])
        if os.path.isdir(src): shutil.copytree(src, os.path.join(OUT, 'course', c['id']))
    open(os.path.join(OUT, '.nojekyll'), 'w').close()

    def url(lang, path):  # path like '' / 'archive/' / 'p/id/'
        return ('/fa/' if lang == 'fa' else '/') + path
    def other(lang): return 'fa' if lang == 'en' else 'en'
    def tr(lang, d): return d[0] if lang == 'en' else d[1]
    def pick(d, lang):  # text with fallback to the other language
        return d.get(lang) or d.get(other(lang)) or ''
    def imgs(p, lang):
        lst = p['images'].get(lang) or p['images'].get(other(lang)) or []
        return lst
    def imgurl(p, stem, suffix=''):
        ext = 'jpg' if suffix in ('-og', '-x') else 'webp'
        return f"/img/{p['id']}/{stem}{suffix}.{ext}"

    def write(rel, content):
        fp = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, 'w', encoding='utf8').write(content)

    # ---------------------------------------------------------- layout
    def layout(lang, path, title, body, desc='', og='/assets/og-default.jpg', page_class='', extra_head='', alt_path=None):
        t = S[lang]; o = other(lang); apath = path if alt_path is None else alt_path
        full_title = title if title == t['name'] else f"{title} · {t['name']}"
        desc = desc or t['tag']
        nav = [('', t['home']), ('archive/', t['archive']), ('specials/', t['specials']), ('evening/', t['evening']), ('notes/', t['notes']), ('pahlavi/', t['pahlavi']), ('course/', t['course']), ('about/', t['about'])]
        navh = ''.join(f'<a href="{url(lang, h)}"{" aria-current=page" if (h == path.split("#")[0] and h != "") or (h == "" and path == "") or (h == "course/" and path.startswith("course/")) else ""}>{E(l)}</a>' for h, l in nav)
        soc = ''
        for k, lbl in (('x', 'X'), ('instagram', 'Instagram'), ('patreon', 'Patreon')):
            if social.get(k): soc += f'<a href="{E(social[k])}" rel="me noopener" target="_blank">{lbl}</a>'
        link_alt = f'<link rel="alternate" hreflang="{o}" href="{SITE}{url(o, apath)}"><link rel="alternate" hreflang="{lang}" href="{SITE}{url(lang, path)}">'
        return f'''<!doctype html>
<html lang="{lang}" dir="{t['dir']}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc[:300])}">
<link rel="canonical" href="{SITE}{url(lang, path)}">{link_alt}
<meta property="og:site_name" content="{E(t['name'])}"><meta property="og:type" content="website">
<meta property="og:title" content="{E(full_title)}"><meta property="og:description" content="{E(desc[:300])}">
<meta property="og:image" content="{SITE}{og}"><meta property="og:url" content="{SITE}{url(lang, path)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="{E(cfg['handle'])}">
<meta name="theme-color" content="#1f2430">
<link rel="icon" href="/assets/favicon.png"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="{E(t['name'])}" href="{url(lang, 'feed.xml')}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Estedad:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">{extra_head}
</head>
<body class="{page_class}">
<a class="skip" href="#main">{E(t['skip'])}</a>
<header class="top"><div class="wrap bar">
 <a class="brand" href="{url(lang, '')}"><img src="/assets/logo.svg" alt="" width="52" height="27"><span>{E(t['name'])}</span></a>
 <nav class="nav" id="nav" aria-label="Main">{navh}</nav>
 <div class="tools"><a class="lang" href="{url(o, apath)}" hreflang="{o}" lang="{o}" title="{E(t['lang_switch_title'])}">{E(t['lang_switch'])}</a>
 <button class="burger" aria-label="{E(t['menu'])}" aria-controls="nav" aria-expanded="false"><span></span><span></span></button></div>
</div></header>
<main id="main">{body}</main>
<footer class="foot"><div class="wrap">
 <div class="fcols"><div><div class="fbrand"><img src="/assets/logo.svg" alt="" width="60" height="31"><b>{E(t['name'])}</b></div><p>{E(t['tag'])}</p></div>
 <div class="flinks"><div class="fh">{E(t['follow'])}</div>{soc}<a href="{url(lang, 'feed.xml')}">{E(t['rss'])}</a></div>
 <div class="flinks"><div class="fh">{E(t['contact'])}</div><a href="mailto:{E(cfg['email'])}">{E(cfg['email'])}</a><span class="muted" dir="ltr">{E(cfg['handle'])}</span></div></div>
 <div class="copy">© {today[:4]} {E(t['name'])} · {E(cfg['author'])}. {E(t['rights'])}</div>
</div></footer>
<script src="/assets/site.js" defer></script>
</body></html>'''

    # ---------------------------------------------------------- components
    def card(p, lang, big=False):
        t = S[lang]; stem = imgs(p, lang)[0]
        ser = tr(lang, SERIES[p['series']]) if p['series'] in SERIES else ''
        topics = ' '.join(p['topics'])
        w, h = (1800, 1012)
        return f'''<a class="card" href="{url(lang, 'p/' + p['id'] + '/')}" data-series="{p['series']}" data-topics="{topics}" data-q="{E((p['title']['en'] + ' ' + p['title']['fa'] + ' ' + ser).lower())}">
 <div class="thumb"><img src="{imgurl(p, stem, '-t')}" alt="{E(p['title'][lang])}" loading="lazy" width="640" height="360"></div>
 <div class="cbody"><div class="cmeta"><span class="chip s-{p['series']}">{E(ser)}</span><time datetime="{p['date']}">{E(fdate(p['date'], lang))}</time></div>
 <h3>{E(p['title'][lang])}</h3></div></a>'''
    def grid(ps, lang): return '<div class="grid">' + ''.join(card(p, lang) for p in ps) + '</div>' if ps else f'<p class="muted">{E(S[lang]["empty"])}</p>'
    def head(lang, title, sub=''):
        return f'<section class="phead"><div class="wrap"><h1>{E(title)}</h1>{f"<p>{E(sub)}</p>" if sub else ""}</div></section>'
    def photos_html(ph, lang):
        if not ph: return ''
        figs = ''
        for x in ph:
            u = f"https://pbs.twimg.com/media/{x['u']}?format=jpg&name=medium"
            cap = f'<figcaption>{E(S[lang]["photo"])}: {E(x["c"])}</figcaption>' if x.get('c') else ''
            figs += f'<figure><a href="{u}" target="_blank" rel="noopener"><img src="{u}" alt="" loading="lazy" referrerpolicy="no-referrer"></a>{cap}</figure>'
        return f'<div class="ephotos n{min(len(ph), 4)}">{figs}</div>'
    def note_card(n, lang):
        txt = (n.get(lang) or n.get(other(lang)) or '').strip()
        return f'<article class="note"><div class="ndate"><time datetime="{n["date"]}">{E(fdate(n["date"], lang))}</time></div><p dir="auto">{para(txt)}</p>{photos_html(n.get("photos"), lang)}<button class="copybtn" data-copy="{E(txt)}" data-done="{E(S[lang]["copied"])}">{E(S[lang]["copyt"])}</button></article>'
    def evening_card(e, lang):
        t = S[lang]
        def blk(k, lbl):
            b = e[k]; txt = b.get(lang) or b.get(other(lang)) or ''
            if not txt: return ''
            body_txt = txt.strip()
            src = f'<div class="src">{E(t["source"])}: {E(b["source"])}</div>' if b.get('source') else ''
            return f'<div class="efact"><div class="elabel">{E(lbl)}</div><p>{para(body_txt)}</p>{src}<button class="copybtn" data-copy="{E(body_txt)}" data-done="{E(t["copied"])}">{E(t["copyt"])}</button>{photos_html(e.get("photos", {}).get(k), lang)}</div>'
        topic = e.get('topic', '')
        return f'<article class="ecard"><div class="ehead"><time datetime="{e["date"]}">{E(fdate(e["date"], lang))}</time></div>{blk("A", t["fact_a"])}{blk("B", t["fact_b"])}</article>'

    # ---------------------------------------------------------- pages
    for lang in ('en', 'fa'):
        t = S[lang]
        # ---- home
        latest = pieces[0] if pieces else None
        body = ''
        if latest:
            stem = imgs(latest, lang)[0]
            cap = pick(latest['caption'], lang)
            body += f'''<section class="hero"><div class="wrap herogrid">
 <div class="herotext"><div class="kicker">{E(t['hero_kicker'])} · {E(fdate(latest['date'], lang))}</div>
 <h1>{E(latest['title'][lang])}</h1><p class="lede">{E(lede(cap))}</p>
 <div class="btns"><a class="btn primary" href="{url(lang, 'p/' + latest['id'] + '/')}">{E(t['view'])}</a><a class="btn" href="{url(lang, 'archive/')}">{E(t['archive'])}</a></div></div>
 <a class="herofig" href="{url(lang, 'p/' + latest['id'] + '/')}"><img src="{imgurl(latest, stem)}" alt="{E(latest['title'][lang])}" width="1800" height="1012" fetchpriority="high"></a>
</div></section>'''
        body += f'<section class="block"><div class="wrap"><div class="shead"><h2>{E(t["latest"])}</h2><a href="{url(lang, "archive/")}">{E(t["see_all"])} →</a></div>{grid(pieces[1:7], lang)}</div></section>'
        # sections teaser
        sp = [p for p in pieces if p['series'] == 'special']; ph = [p for p in pieces if p['series'] == 'pahlavi']
        body += '<section class="block alt"><div class="wrap tri">'
        body += f'<div class="tcard"><h2>{E(t["sec_specials"])}</h2><p>{E(t["sec_specials_d"])}</p>' + (card(sp[0], lang) if sp else '') + f'<a class="more" href="{url(lang, "specials/")}">{E(t["see_all"])} →</a></div>'
        body += f'<div class="tcard"><h2>{E(t["sec_evening"])}</h2><p>{E(t["sec_evening_d"])}</p>' + (evening_card(evening[0], lang) if evening else '') + f'<a class="more" href="{url(lang, "evening/")}">{E(t["see_all"])} →</a></div>'
        body += f'<div class="tcard"><h2>{E(t["sec_pahlavi"])}</h2><p>{E(t["sec_pahlavi_d"])}</p>' + (card(ph[0], lang) if ph else f'<div class="soon">{E(t["coming"])}</div>') + f'<a class="more" href="{url(lang, "pahlavi/")}">{E(t["see_all"])} →</a></div>'
        body += '</div></section>'
        used = sorted({tp for p in pieces for tp in p['topics']})
        body += f'<section class="block"><div class="wrap"><div class="shead"><h2>{E(t["sec_topics"])}</h2></div><div class="chips">' + ''.join(f'<a class="chip big" href="{url(lang, "archive/")}#topic={tp}">{E(tr(lang, TOPICS[tp]))}</a>' for tp in used) + '</div></div></section>'
        write(url(lang, '').lstrip('/') + 'index.html', layout(lang, '', t['name'], body, t['tag'], og=imgurl(latest, imgs(latest, lang)[0], '-og') if latest else '/assets/og-default.jpg', page_class='home'))

        # ---- archive
        sers = [s for s in SERIES if any(p['series'] == s for p in pieces)]
        tops = [tp for tp in TOPICS if any(tp in p['topics'] for p in pieces)]
        filt = f'''<div class="filters"><input type="search" id="q" placeholder="{E(t['search'])}" aria-label="{E(t['search'])}">
<div class="fgroup" data-key="series"><span>{E(t['series'])}</span><button class="on" data-v="">{E(t['all'])}</button>''' + ''.join(f'<button data-v="{s}">{E(tr(lang, SERIES[s]))}</button>' for s in sers) + f'''</div>
<div class="fgroup" data-key="topic"><span>{E(t['topic'])}</span><button class="on" data-v="">{E(t['all'])}</button>''' + ''.join(f'<button data-v="{x}">{E(tr(lang, TOPICS[x]))}</button>' for x in tops) + f'''</div>
<div class="count"><b id="n">{fa_digits(len(pieces)) if lang == 'fa' else len(pieces)}</b> {E(t['results'])}</div></div>'''
        body = head(lang, t['archive']) + f'<section class="block"><div class="wrap">{filt}<div id="archive">{grid(pieces, lang)}</div></div></section>'
        write(url(lang, 'archive/').lstrip('/') + 'index.html', layout(lang, 'archive/', t['archive'], body, page_class='archive'))

        # ---- specials / pahlavi
        sp = [p for p in pieces if p['series'] == 'special']
        write(url(lang, 'specials/').lstrip('/') + 'index.html', layout(lang, 'specials/', t['specials'], head(lang, t['specials'], t['sec_specials_d']) + f'<section class="block"><div class="wrap">{grid(sp, lang)}</div></section>'))
        ph = [p for p in pieces if p['series'] == 'pahlavi']
        write(url(lang, 'pahlavi/').lstrip('/') + 'index.html', layout(lang, 'pahlavi/', t['pahlavi'], head(lang, t['pahlavi'], t['sec_pahlavi_d']) + f'<section class="block"><div class="wrap">' + (grid(ph, lang) if ph else f'<div class="soon big">{E(t["coming"])}</div>') + '</div></section>'))
        # ---- evening
        write(url(lang, 'evening/').lstrip('/') + 'index.html', layout(lang, 'evening/', t['evening'], head(lang, t['evening'], t['sec_evening_d']) + '<section class="block"><div class="wrap evlist">' + (''.join(evening_card(e, lang) for e in evening) or f'<p class="muted">{E(t["empty"])}</p>') + '</div></section>'))
        # ---- notes
        groups = ''
        for key, nm in NOTE_TOPICS.items():
            ns = [n for n in notes if n['topic'] == key]
            if ns: groups += f'<section class="block"><div class="wrap"><div class="shead"><h2>{E(tr(lang, nm))}</h2></div><div class="notelist">' + ''.join(note_card(n, lang) for n in ns) + '</div></div></section>'
        write(url(lang, 'notes/').lstrip('/') + 'index.html', layout(lang, 'notes/', t['notes'], head(lang, t['notes'], t['sec_notes_d']) + (groups or f'<section class="block"><div class="wrap"><p class="muted">{E(t["empty"])}</p></div></section>')))
        # ---- about
        ab = ''.join(f'<p>{E(x)}</p>' for x in t['about_p']) + f'<h2>{E(t["about_h2"][0])}</h2><ul>' + ''.join(f'<li>{E(x)}</li>' for x in t['about_list']) + f'</ul><h2>{E(t["about_h2"][1])}</h2><div class="btns">'
        for k, lbl in (('x', 'X'), ('instagram', 'Instagram'), ('patreon', 'Patreon')):
            if social.get(k): ab += f'<a class="btn" href="{E(social[k])}" rel="me noopener" target="_blank">{lbl}</a>'
        ab += f'<a class="btn" href="mailto:{E(cfg["email"])}">{E(cfg["email"])}</a></div>'
        write(url(lang, 'about/').lstrip('/') + 'index.html', layout(lang, 'about/', t['about_title'], head(lang, t['about_title'], t['tag']) + f'<section class="block"><div class="wrap prose">{ab}</div></section>'))

        # ---- piece pages
        for i, p in enumerate(pieces):
            stems = imgs(p, lang); ostems = p['images'].get(other(lang)) or []
            cap = pick(p['caption'], lang); alt = pick(p['alt'], lang) or p['title'][lang]
            same = (p['images']['en'] == p['images']['fa']) or not ostems or not stems
            figs = ''
            for n, st in enumerate(stems):
                a_ = alt if len(stems) == 1 else f"{alt} ({n+1}/{len(stems)})"
                oalt = pick(p['alt'], other(lang)) or p['title'][other(lang)]
                ost = ostems[n] if n < len(ostems) else st
                figs += f'<figure class="fig"><a class="zoom" href="{imgurl(p, st)}" data-full="{imgurl(p, st)}"><img src="{imgurl(p, st)}" alt="{E(a_)}" width="1800" height="1012" data-l="{lang}" data-src-{lang}="{imgurl(p, st)}" data-src-{other(lang)}="{imgurl(p, ost)}" data-alt-{lang}="{E(a_)}" data-alt-{other(lang)}="{E(oalt)}"{" fetchpriority=high" if n == 0 else ""}></a></figure>'
            dl = ''.join(f'<a class="btn primary" href="{imgurl(p, st, "-x")}" download>{E(t["download"])}{f" {n+1}" if len(stems) > 1 else ""}</a>' for n, st in enumerate(stems))
            tabs = ''
            if not same:
                tabs = f'<div class="seg" role="group" aria-label="{E(t["infolang"])}"><span>{E(t["infolang"])}</span><button data-l="en"{" class=on" if lang == "en" else ""}>EN</button><button data-l="fa"{" class=on" if lang == "fa" else ""}>FA</button></div>'
            ser = tr(lang, SERIES[p['series']]) if p['series'] in SERIES else ''
            chips = f'<span class="chip s-{p["series"]}">{E(ser)}</span>' + ''.join(f'<a class="chip" href="{url(lang, "archive/")}#topic={x}">{E(tr(lang, TOPICS[x]))}</a>' for x in p['topics'] if x in TOPICS)
            share_txt = re.sub(r'\s+', ' ', cap)[:200]
            share = 'https://x.com/intent/post?text=' + __import__('urllib.parse').parse.quote(f"{p['title'][lang]} — {cfg['handle']}") + '&url=' + __import__('urllib.parse').parse.quote(SITE + url(lang, 'p/' + p['id'] + '/'))
            takes = ''
            tk = p['posts'].get(lang) or p['posts'].get(other(lang)) or []
            if tk:
                takes = f'<section class="sec"><h2>{E(t["takes"])}</h2><div class="takes">' + ''.join(f'<div class="take"><p dir="auto">{para(x)}</p><button class="copybtn" data-copy="{E(x)}" data-done="{E(t["copied"])}">{E(t["copyt"])}</button></div>' for x in tk) + '</div></section>'
            sib = [q for q in pieces if q['series'] == p['series'] and q['id'] != p['id']]
            sib.sort(key=lambda q: abs((datetime.date.fromisoformat(q['date']) - datetime.date.fromisoformat(p['date'])).days))
            more = f'<section class="block alt"><div class="wrap"><div class="shead"><h2>{E(t["more"])}</h2></div>{grid(sib[:3], lang)}</div></section>' if sib else ''
            nxt = pieces[i - 1] if i > 0 else None; prv = pieces[i + 1] if i + 1 < len(pieces) else None
            pn = '<nav class="pn">' + (f'<a href="{url(lang, "p/" + prv["id"] + "/")}"><small>{E(t["prev"])}</small>{E(prv["title"][lang])}</a>' if prv else '<span></span>') + (f'<a class="r" href="{url(lang, "p/" + nxt["id"] + "/")}"><small>{E(t["next"])}</small>{E(nxt["title"][lang])}</a>' if nxt else '<span></span>') + '</nav>'
            capblk = f'<section class="sec"><h2>{E(t["caption"])}</h2><p class="cap" dir="auto">{para(cap)}</p><button class="copybtn" data-copy="{E(cap)}" data-done="{E(t["copied"])}">{E(t["copy"])}</button></section>' if cap else ''
            altblk = f'<details class="sec altd"><summary>{E(t["alt"])}</summary><p id="alttext" dir="auto">{E(alt)}</p></details>' if pick(p['alt'], lang) else ''
            body = f'''<article class="piece"><div class="wrap">
<div class="crumb"><a href="{url(lang, '')}">{E(t['home'])}</a> / <a href="{url(lang, 'archive/')}">{E(t['archive'])}</a></div>
<header class="ph"><div class="chips">{chips}<time datetime="{p['date']}">{E(fdate(p['date'], lang))}</time></div><h1>{E(p['title'][lang])}</h1></header>
{tabs}<div class="figs">{figs}</div>
<div class="btns act">{dl}<a class="btn" href="{E(share)}" target="_blank" rel="noopener">{E(t['share'])}</a></div>
<div class="cols"><div>{capblk}{takes}</div><div>{altblk}</div></div>
{pn}</div></article>{more}'''
            ld = {'@context': 'https://schema.org', '@type': 'ImageObject', 'name': p['title'][lang], 'contentUrl': SITE + imgurl(p, stems[0]), 'datePublished': p['date'], 'creator': {'@type': 'Person', 'name': cfg['author']}, 'caption': alt}
            xh = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
            write(url(lang, 'p/' + p['id'] + '/').lstrip('/') + 'index.html', layout(lang, 'p/' + p['id'] + '/', p['title'][lang], body, re.sub(r'#\S+', '', cap).strip(), og=imgurl(p, stems[0], '-og'), page_class='piecepage', extra_head=xh))

        # ---- course
        if course:
            pat = social.get('patreon', '')
            pad = lambda i: f'{i:02d}'
            nfmt = (lambda x: fa_digits(x)) if lang == 'fa' else (lambda x: str(x))
            total = sum(c['n'] for c in course)
            cards = ''
            for c in course:
                cards += f'<a class="mcard" style="--ac:{c["accent"]}" href="/course/{c["id"]}/"><div class="thumb"><img src="/course/{c["id"]}/cover.webp" alt="{E(c["title"])}" width="960" height="540" loading="lazy"></div><div class="cb"><div class="mnum">{E(t["mod"])} {nfmt(c["num"])}</div><h3 dir="ltr" lang="en">{E(c["title"])}</h3><p dir="ltr" lang="en">{E(c["desc"])}</p><div class="meta"><span class="chip">{nfmt(c["n"])} {E(t["slides"])}</span><span class="chip">PDF</span></div></div></a>'
            who = ''.join(f'<li>{E(x)}</li>' for x in t['course_who'])
            intro = f'<div class="cintro"><div><ul>{who}</ul></div><div class="cnote"><b>{E(t["course_note_h"])}</b>{E(t["course_note"])}</div></div>'
            body = head(lang, t['course_h'], t['course_d']) + f'<section class="block"><div class="wrap">{intro}</div></section><section class="block alt"><div class="wrap"><div class="cgrid">{cards}</div></div></section>'
            write(url(lang, 'course/').lstrip('/') + 'index.html', layout(lang, 'course/', t['course_h'], body, t['course_d'], og=f'/course/{course[0]["id"]}/cover.webp', page_class='coursepage', extra_head='<link rel="stylesheet" href="/assets/course.css">'))
            if lang == 'en':
                for ci, c in enumerate(course):
                    base = f'/course/{c["id"]}/'
                    pdf = f'{base}{c["stem"]}.pdf'
                    parts = ''.join(f'<a href="#{pi}" data-go="{pi}">{E(pt)}</a>' for pi, pt in c['parts'])
                    tg = ''.join(f'<button class="tg" type="button" aria-label="Slide {i+1}: {E(tt)}"><img src="{base}t/{pad(i+1)}.webp" alt="" width="320" height="180" loading="lazy"><span>{i+1}. {E(tt)}</span></button>' for i, tt in enumerate(c['titles']))
                    pb = f'<a class="btn pat" href="{E(pat)}" rel="noopener" target="_blank">{E(t["pptx_pat"])}</a>' if pat else ''
                    prv = course[ci-1] if ci > 0 else None; nx = course[ci+1] if ci+1 < len(course) else None
                    mn = '<div class="mnav">' + (f'<a href="/course/{prv["id"]}/"><small>{E(t["prev"])}</small>{E(t["mod"])} {prv["num"]}: {E(prv["title"])}</a>' if prv else '<span></span>') + (f'<a class="r" href="/course/{nx["id"]}/"><small>{E(t["next"])}</small>{E(t["mod"])} {nx["num"]}: {E(nx["title"])}</a>' if nx else '<span></span>') + '</div>'
                    body = f"""<section class="mhero"><div class="wrap"><div><div class="kicker">{E(t["mod"])} {c["num"]} / {len(course)} · {c["n"]} {E(t["slides"])}</div><h1>{E(c["title"])}</h1><p>{E(c["desc"])}</p><div class="mbtns"><a class="btn ac" href="#viewer">{E(t["read_on"])}</a><a class="btn primary" href="{pdf}" download>{E(t["dl_pdf"])}</a>{pb}</div></div><div class="cov"><img src="{base}cover.webp" alt="{E(c["title"])}, cover" width="960" height="540"></div></div></section>
<section class="block"><div class="wrap"><div class="crumb"><a href="/">{E(t["home"])}</a> / <a href="/course/">{E(t["course_h"])}</a></div>
<div class="parts" aria-label="{E(t["parts_h"])}">{parts}</div>
<div class="viewer" id="viewer" data-base="{base}" data-n="{c["n"]}" data-name="{E(t["mod"])} {c["num"]}" data-titles="{E(json.dumps(c["titles"], ensure_ascii=False))}">
<div class="vstage" id="vstage"><img id="vimg" src="{base}s/01.webp" alt="" width="1440" height="810"></div>
<div class="vbar"><button class="vbtn" id="vprev" type="button">← {E(t["prev_s"])}</button><div class="vt" id="vt"></div><span class="vc" id="vc"></span><button class="vbtn" id="vfull" type="button">{E(t["fullscr"])}</button><button class="vbtn ac" id="vnext" type="button">{E(t["next_s"])} →</button></div></div>
<h2 style="margin-top:34px">{E(t["contents"])}</h2><div class="tgrid">{tg}</div>{mn}</div></section>"""
                    ldc = {'@context': 'https://schema.org', '@type': 'Course', 'name': c['title'], 'description': c['desc'], 'provider': {'@type': 'Organization', 'name': t['name'], 'sameAs': SITE}, 'inLanguage': 'en', 'isAccessibleForFree': True}
                    write(f'course/{c["id"]}/index.html', layout('en', f'course/{c["id"]}/', f'{t["mod"]} {c["num"]}: {c["title"]}', body, c['desc'], og=f'{base}cover.webp', page_class='coursepage', extra_head='<link rel="stylesheet" href="/assets/course.css"><script src="/assets/course.js" defer></script><script type="application/ld+json">' + json.dumps(ldc, ensure_ascii=False) + '</script>', alt_path='course/'))

        # ---- RSS
        items = ''
        for p in pieces[:40]:
            st = imgs(p, lang)[0]; cap = pick(p['caption'], lang)
            items += f'<item><title>{xesc(p["title"][lang])}</title><link>{SITE}{url(lang, "p/" + p["id"] + "/")}</link><guid>{SITE}{url(lang, "p/" + p["id"] + "/")}</guid><pubDate>{rfc822(p["date"])}</pubDate><description>{xesc(cap)}</description><enclosure url="{SITE}{imgurl(p, st, "-og")}" type="image/jpeg" length="0"/></item>'
        write(url(lang, 'feed.xml').lstrip('/'), f'<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>{xesc(t["name"])}</title><link>{SITE}{url(lang, "")}</link><description>{xesc(t["tag"])}</description><language>{lang}</language>{items}</channel></rss>')

    # ---------------------------------------------------------- sitemap, robots, 404
    urls = []
    for lang in ('en', 'fa'):
        for pth in ['', 'archive/', 'specials/', 'evening/', 'notes/', 'pahlavi/', 'about/'] + ['course/'] + [f"p/{p['id']}/" for p in pieces] + ([f"course/{c['id']}/" for c in course] if lang == 'en' else []):
            urls.append(SITE + url(lang, pth))
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{u}</loc></url>' for u in urls) + '</urlset>')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    write('404.html', layout('en', '', 'Page not found', '<section class="phead"><div class="wrap"><h1>Page not found</h1><p><a href="/">Home</a> · <a href="/fa/">فارسی</a></p></div></section>'))
    print(f'built {len(pieces)} pieces, {len(evening)} evening entries, today={today} -> {OUT}')

if __name__ == '__main__':
    main()
