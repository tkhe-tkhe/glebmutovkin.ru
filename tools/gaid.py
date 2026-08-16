# Конвертер исходника гайда в тело + мету сайта.
#
#   python3 tools/gaid.py <исходник.html> <slug>
#
# Исходники гайдов свёрстаны по-разному: у одного разделы — h1 подряд,
# у другого — группы h1, внутри карточки <article class='plugin-card'>.
# Опираемся на заголовки и на известные классы генератора, всё остальное
# разворачиваем в плоский поток.
#
# Кладёт:
#   src/content/gaidy/<slug>.html     тело
#   src/data/gaidy/<slug>.json        мета, оглавление, источники
#   src/images/gaidy/<slug>/NN.png    картинки, вынутые из base64
#
# Название и подводку берём с обложки исходника — их можно поправить руками
# в json, вёрстка от этого не зависит.

import base64
import html
import json
import os
import re
import sys

ISHODNIK, SLUG = sys.argv[1], sys.argv[2]
KOREN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(KOREN, 'src/images/gaidy', SLUG)

s = open(ISHODNIK, encoding='utf-8').read()

# --- обложка: название, подводка, подпись ------------------------------------
oblozhka = re.search(r"<section class='cover'>(.*?)</section>", s, re.S)
# из разметки в чистый текст: снять теги и раскрыть сущности,
# иначе в оглавление уезжает «Preamp &amp; EQ»
tekst = lambda x: html.unescape(re.sub(r'<[^>]+>', '', x or '')).strip()
nazvanie = podvodka = ''
if oblozhka:
    o = oblozhka.group(1)
    nazvanie = tekst(re.search(r'<h1>(.*?)</h1>', o, re.S).group(1))
    h2 = re.search(r'<h2>(.*?)</h2>', o, re.S)
    podvodka = tekst(h2.group(1)) if h2 else ''
    # обложка иногда набрана капслоком («UAD PLUG-INS») — в каталоге сайта это
    # крик. Тогда берём написание из <title> документа, до тире.
    if nazvanie == nazvanie.upper():
        zag = re.search(r'<title>(.*?)</title>', s, re.S)
        if zag:
            nazvanie = tekst(zag.group(1)).split('—')[0].strip()

# --- картинки: base64 -> файлы, в теле остаётся метка IMG:NN ------------------
os.makedirs(IMG_DIR, exist_ok=True)
kartinki = []


def vynut(m):
    tag = m.group(0)
    d = re.search(r"src=['\"]data:image/([a-z+]+);base64,([^'\"]+)['\"]", tag)
    if not d:
        return tag
    n = len(kartinki) + 1
    imya = f'{n:02d}.{"jpg" if d.group(1) == "jpeg" else d.group(1)}'
    open(os.path.join(IMG_DIR, imya), 'wb').write(base64.b64decode(d.group(2)))
    kartinki.append(imya)
    alt = re.search(r"alt=['\"]([^'\"]*)", tag)
    return f'<img src="IMG:{n:02d}" alt="{html.escape(alt.group(1)) if alt else ""}">'


s = re.sub(r'<img[^>]*>', vynut, s)

# --- отрезаем всё, что заменяется оснасткой сайта ------------------------------
s = re.sub(r'<nav>.*?</nav>', '', s, flags=re.S)                 # своё оглавление
s = re.sub(r"<section class='cover'>.*?</section>", '', s, flags=re.S)
s = re.sub(r"<a class='top'.*?</a>", '', s, flags=re.S)          # кнопка «наверх»
s = re.sub(r'<input[^>]*>', '', s)                               # свой поиск по гайду
s = re.sub(r"<p id='empty'.*?</p>", '', s, flags=re.S)
telo = s[s.find('<h1'):s.rfind('</main>')]

# --- источники: свой блок внизу ------------------------------------------------
i = telo.find("<h1 id='sources'")
hvost, telo = telo[i:], telo[:i]

svepka = re.search(r'<p>(.*?)</p>', hvost, re.S)
istochniki = {}
for m in re.finditer(
    r"<div class='source' id='src-([^']+)'><strong>[^<]+</strong>\s*—\s*(.*?)"
    r"<a href='([^']+)'>.*?</a></div>",
    hvost,
    re.S,
):
    kod, nazv, url = m.group(1), m.group(2).strip().rstrip(':').strip(), m.group(3)
    istochniki[kod] = {'title': re.sub(r'<[^>]+>', '', nazv), 'url': url}

# --- карточки: у каждой свой id, по нему строится второй уровень оглавления ----
karty = []
for m in re.finditer(
    r"<article class='plugin-card' id='([^']+)'[^>]*>\s*<h2>(.*?)</h2>", telo, re.S
):
    karty.append({'id': m.group(1), 'label': tekst(m.group(2))})

telo = re.sub(r"<article class='plugin-card' id='([^']+)'[^>]*>", r'<section id="\1">', telo)
telo = telo.replace('</article>', '</section>')
telo = re.sub(r"<section class='category'>", '<section>', telo)
telo = re.sub(r"<span class='status'>(.*?)</span>", r'<div class="status">\1</div>', telo,
              flags=re.S)

# --- заголовки на уровень ниже: h1 исходника = раздел = h2 на сайте -----------
telo = re.sub(r'<(/?)h3([ >])', r'<\1h4\2', telo)
telo = re.sub(r'<(/?)h2([ >])', r'<\1h3\2', telo)
telo = re.sub(r'<(/?)h1([ >])', r'<\1h2\2', telo)


# --- врезки: коробку с заливкой заменяем выноской с левой линией --------------
def vrezka(m):
    tip, vnutri = m.group(1) or '', m.group(2)
    zagolovok = re.match(r'\s*<strong>(.*?)</strong>', vnutri, re.S)
    metka = tekst(zagolovok.group(1)).rstrip('.') if zagolovok else ''
    if zagolovok:
        vnutri = vnutri[zagolovok.end():]
    if '<p' not in vnutri and '<ul' not in vnutri:
        vnutri = f'<p>{vnutri.strip()}</p>'
    klass = 'note stop' if tip.strip() in ('danger', 'warning') else 'note'
    return f'<div class="{klass}">' + (f'<b>{metka}</b>' if metka else '') + vnutri + '</div>'


telo = re.sub(r"<(?:aside|div) class='callout ?([a-z]*)'>(.*?)</(?:aside|div)>", vrezka, telo,
              flags=re.S)

# --- таблицы, пути в интерфейсе, сноски, ссылки -------------------------------
telo = telo.replace("<div class='table-wrap'>", '<div class="tbl">')
telo = re.sub(r"<span class='app'>(.*?)</span>", r'<code class="ui">\1</code>', telo, flags=re.S)
telo = re.sub(
    r'<a class="cite" href="#src-([^"]+)">\[[^\]]+\]</a>',
    r'<a class="ref" href="#src-\1">\1</a>',
    telo,
)
telo = re.sub(
    r"<a href='(https?://[^']+)'>",
    r'<a class="link" href="\1" target="_blank" rel="noopener">',
    telo,
)
telo = telo.replace('<figure>', '<figure class="risunok">')
telo = re.sub(r"'", '"', telo)  # исходник в одинарных кавычках, приводим к одному виду

# --- список источников внизу ---------------------------------------------------
punkty = ''.join(
    f'<li id="src-{kod}"><span class="sn">{kod}</span><div>{html.escape(v["title"])}'
    f'<a class="link" href="{v["url"]}" target="_blank" rel="noopener">{v["url"]}</a></div></li>'
    for kod, v in istochniki.items()
)
telo += (
    '<h2 id="istochniki">Источники</h2>'
    + (f'<div class="note"><p>{tekst(svepka.group(1))}</p></div>' if svepka else '')
    + f'<ol class="srclist">{punkty}</ol>'
)

# --- оглавление: разделы и, если есть, карточки внутри них --------------------
karty_po_id = {k['id']: k for k in karty}
toc = []
# два узора в одном проходе, чтобы порядок в оглавлении совпадал с порядком
# в тексте. Раздельно: общий узор с необязательной группой съедал текст
# до следующего </h2> и терял двадцать карточек из двадцати девяти.
for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>|<section id="([^"]+)">', telo, re.S):
    if m.group(1):
        toc.append({'href': '#' + m.group(1), 'label': tekst(m.group(2)), 'uroven': 1})
    elif m.group(3) in karty_po_id:
        toc.append({'href': '#' + m.group(3), 'label': karty_po_id[m.group(3)]['label'],
                    'uroven': 2})

slov = len(re.sub(r'<[^>]+>', ' ', telo).split())

meta = {
    'slug': SLUG,
    'title': nazvanie,
    'lede': podvodka,
    'oblast': 'звук',
    'data': 'Август 2026',
    'god': '2026',
    'toc': toc,
    'istochniki': istochniki,
    'slov': slov,
    'min': max(1, round(slov / 160)),
}

os.makedirs(os.path.join(KOREN, 'src/content/gaidy'), exist_ok=True)
os.makedirs(os.path.join(KOREN, 'src/data/gaidy'), exist_ok=True)
open(os.path.join(KOREN, f'src/content/gaidy/{SLUG}.html'), 'w', encoding='utf-8').write(telo)
open(os.path.join(KOREN, f'src/data/gaidy/{SLUG}.json'), 'w', encoding='utf-8').write(
    json.dumps(meta, ensure_ascii=False, indent=1)
)

print(f'{SLUG}: разделов {sum(1 for t in toc if t["uroven"] == 1)}',
      f'· карточек {sum(1 for t in toc if t["uroven"] == 2)}',
      f'· источников {len(istochniki)} · слов {slov} · картинок {len(kartinki)}')
