# Конвертер многостраничного разбора — «тома».
#
#   python3 tools/tom.py <исходник.html> <slug>
#
# Обычный разбор — одна страница: 3000 слов, оглавление из десяти пунктов.
# Том так не читается. «Царская семья» — 139 000 слов, 11 частей, 96 таблиц:
# одной страницей это 2 МБ разметки и оглавление из 54 пунктов без вложенности.
# Поэтому здесь исходник режется на страницы: обложка, части, а часть, которая
# сама по себе больше самого большого разбора, — по своим разделам.
#
# Кладёт:
#   src/content/toma/<slug>/<страница>.html   тела страниц
#   src/data/toma/<slug>.json                 мета, разбивка, оглавления
#
# Название, подводку, область и текст плашки скрипту взять неоткуда — их
# вписывают руками в JSON, следующий прогон их сохранит (как у справочника
# в tools/gaid.py).
#
# Исходник — вывод pandoc: h1 части, h2 разделы, h3/h4 подразделы,
# боковое оглавление <nav id="TOC">, якоря вида s08h001.

import html
import json
import os
import re
import sys

ISHODNIK, SLUG = sys.argv[1], sys.argv[2]
KOREN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Часть длиннее этого режется по своим разделам. Ориентир — самый большой
# разбор собрания, «Человек перед Богом»: 14 209 слов. Всё, что больше,
# на одной странице читать нечем.
PREDEL_CHASTI = 15000

# Второй уровень оглавления (подразделы) показываем, пока список не разросся.
PREDEL_TOC = 70

PUT_META = os.path.join(KOREN, f'src/data/toma/{SLUG}.json')
BYLO = json.load(open(PUT_META, encoding='utf-8')) if os.path.exists(PUT_META) else {}

# pandoc переносит строки внутри заголовков — в оглавлении сайта такой
# заголовок разорвался бы посреди слова, поэтому пробелы схлопываем
tekst = lambda x: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', x or ''))).strip()
slov_v = lambda x: len(re.sub(r'<[^>]+>', ' ', x).split())

# --- перевод названия в адрес ------------------------------------------------
# Адрес страницы получается из её заголовка: он осмысленный и переживает
# правку соседних разделов, чего не скажешь о номерах вида s08 из исходника —
# вставил раздел в середину, и все адреса после него уехали.
BUKVY = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
    'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def adres(nazvanie, zanyato):
    # до двоеточия: у разделов хронологии после него идут даты
    # («Тобольск в октябре: 1/14–31 октября…») — в адресе они лишние
    osnova = nazvanie.split(':')[0]
    osnova = re.sub(r'^Часть\s+[IVX]+\.\s*', '', osnova)
    put = ''.join(BUKVY.get(z, z) for z in osnova.lower())
    put = re.sub(r'[^a-z0-9]+', '-', put).strip('-')
    slova, itog = put.split('-'), []
    for sl in slova:
        if itog and len('-'.join(itog + [sl])) > 46:
            break
        itog.append(sl)
    # предлог на конце адреса («…-semi-vmeste-v») выглядит как обрыв
    while len(itog) > 1 and len(itog[-1]) <= 2:
        itog.pop()
    put = '-'.join(itog) or 'stranica'
    if put in zanyato:                       # одинаковые заголовки в разных частях
        n = 2
        while f'{put}-{n}' in zanyato:
            n += 1
        put = f'{put}-{n}'
    zanyato.add(put)
    return put


# --- тело исходника ----------------------------------------------------------
s = open(ISHODNIK, encoding='utf-8').read()
telo = s[s.find('<body') :]
telo = telo[telo.find('>') + 1 : telo.rfind('</body>')]
# Название и подзаголовок стоят в шапке pandoc — забираем их до того,
# как шапку срезать: на сайте её рисует каркас страницы.
shapka = re.search(r'<header id="title-block-header".*?</header>', telo, flags=re.S)
nazvanie_ishodnika = podzagolovok = ''
if shapka:
    zag = re.search(r'<h1[^>]*class="title"[^>]*>(.*?)</h1>', shapka.group(0), re.S)
    pod = re.search(r'<p class="subtitle">(.*?)</p>', shapka.group(0), re.S)
    nazvanie_ishodnika = tekst(zag.group(1)) if zag else ''
    podzagolovok = tekst(pod.group(1)) if pod else ''

telo = re.sub(r'<header id="title-block-header".*?</header>', '', telo, flags=re.S)
telo = re.sub(r'<nav id="TOC".*?</nav>', '', telo, flags=re.S)   # оглавление даёт сайт

# версия тома: либо словом в тексте, либо «_v1.1_» в имени файла
versiya = re.search(r'[Вв]ерсия[^0-9]{0,12}([0-9]+\.[0-9]+)', s[:6000]) or re.search(
    r'[_-]v([0-9]+\.[0-9]+)', os.path.basename(ISHODNIK)
)

# --- режем по h1 -------------------------------------------------------------
bloki, granicy = [], [m for m in re.finditer(r'<h1([^>]*)>(.*?)</h1>', telo, re.S)]
for i, m in enumerate(granicy):
    konec = granicy[i + 1].start() if i + 1 < len(granicy) else len(telo)
    yakor = re.search(r'id="([^"]+)"', m.group(1))
    bloki.append({'zagolovok': tekst(m.group(2)),
                  'id': yakor.group(1) if yakor else '',
                  'telo': telo[m.end() : konec]})

# До первой «Части» идут вводные разделы — они уходят на обложку.
vvodnye = [b for b in bloki if not b['zagolovok'].startswith('Часть')]
chasti_ish = [b for b in bloki if b['zagolovok'].startswith('Часть')]

if not chasti_ish:
    print('  ВНИМАНИЕ: в исходнике нет заголовков «Часть …» — резать нечего')
    sys.exit(1)


# --- чистка разметки ---------------------------------------------------------
def pochistit(kusok):
    # ширины колонок от pandoc: на телефоне они ломают таблицу сильнее,
    # чем её отсутствие
    kusok = re.sub(r'<colgroup>.*?</colgroup>', '', kusok, flags=re.S)
    # голая таблица тянет горизонтальную прокрутку всей страницы — обернуть
    kusok = re.sub(r'<table[^>]*>(.*?)</table>',
                   r'<div class="tbl"><table>\1</table></div>', kusok, flags=re.S)
    kusok = re.sub(r'<a href="(https?://[^"]+)"[^>]*>',
                   r'<a class="link" href="\1" target="_blank" rel="noopener">', kusok)
    return kusok


# --- собираем страницы -------------------------------------------------------
# Страница — это либо обложка, либо часть целиком, либо один раздел большой
# части. Внутри разрезанной части подразделы поднимаются на уровень выше:
# заголовок раздела рисует каркас страницы, поэтому текст должен начинаться
# с h2, а не с h3, иначе оглавление страницы окажется пустым.
zanyato = set()
stranicy = []      # плоский список в порядке чтения
chasti = []        # то же, сгруппированное по частям, — для оглавления тома

for b in chasti_ish:
    nomer, _, nazv = b['zagolovok'].removeprefix('Часть').strip().partition('.')
    nazv = nazv.strip() or b['zagolovok']
    razdely = [m for m in re.finditer(r'<h2([^>]*)>(.*?)</h2>', b['telo'], re.S)]

    if slov_v(b['telo']) <= PREDEL_CHASTI or len(razdely) < 2:
        strs = [{'label': nazv, 'telo': b['telo'], 'podnyat': False, 'yakor': b['id']}]
    else:
        strs = []
        for i, m in enumerate(razdely):
            konec = razdely[i + 1].start() if i + 1 < len(razdely) else len(b['telo'])
            yakor = re.search(r'id="([^"]+)"', m.group(1))
            strs.append({'label': tekst(m.group(2)), 'yakor': yakor.group(1) if yakor else '',
                         'telo': b['telo'][m.end() : konec], 'podnyat': True})
        # текст, стоящий до первого раздела, приклеиваем к первой странице
        shapka = b['telo'][: razdely[0].start()]
        if tekst(shapka):
            strs[0]['telo'] = shapka + strs[0]['telo']

    svoi = []
    for st in strs:
        st['slug'] = adres(st['label'], zanyato)
        st['chast'] = {'nomer': nomer.strip(), 'nazv': nazv}
        stranicy.append(st)
        svoi.append(st)
    chasti.append({'nomer': nomer.strip(), 'nazv': nazv, 'stranicy': svoi})

# --- карта якорей: какой заголовок на какой странице --------------------------
# В тексте 400 внутренних ссылок вида href="#s24h035". После разрезания
# половина из них указывает на другую страницу, и без переписывания они
# просто ведут в никуда — молча, сборка от этого не падает.
# Вводные разделы исходника набраны h1 наравне с частями. На обложке они —
# обычные разделы страницы, поэтому заголовок опускается до h2, а всё, что
# было внутри, — на уровень ниже.
vvedenie_telo = ''
for b in vvodnye:
    vnutri = re.sub(r'<(/?)h([2-6])([ >])',
                    lambda m: f'<{m.group(1)}h{min(6, int(m.group(2)) + 1)}{m.group(3)}',
                    b['telo'])
    vvedenie_telo += f'<h2 id="{b["id"]}">{html.escape(b["zagolovok"])}</h2>' + vnutri

gde = {}
for m in re.finditer(r'id="([^"]+)"', vvedenie_telo):
    gde[m.group(1)] = ''                      # пусто — значит обложка
for st in stranicy:
    # якорь самого заголовка страницы: тега h2 в теле уже нет, его рисует
    # каркас — но ссылки на него в тексте остались, и он должен вести сюда
    if st['yakor']:
        gde[st['yakor']] = st['slug']
    for m in re.finditer(r'id="([^"]+)"', st['telo']):
        gde.setdefault(m.group(1), st['slug'])


def perepisat(kusok, svoya):
    def ssylka(m):
        cel = m.group(1)
        stranica = gde.get(cel)
        if stranica is None:
            perepisat.bitye.append(cel)
            return m.group(0)
        if stranica == svoya:
            return m.group(0)
        hvost = f'{stranica}/' if stranica else ''
        return f'href="/razbory/{SLUG}/{hvost}#{cel}"'

    return re.sub(r'href="#([^"]+)"', ssylka, kusok)


perepisat.bitye = []

# --- оглавление страницы ------------------------------------------------------
def toc_iz(kusok):
    punkty = []
    for m in re.finditer(r'<h([23])[^>]*id="([^"]+)"[^>]*>(.*?)</h\1>', kusok, re.S):
        punkty.append({'href': '#' + m.group(2), 'label': tekst(m.group(3)),
                       'uroven': 1 if m.group(1) == '2' else 2})
    if len(punkty) > PREDEL_TOC:
        punkty = [p for p in punkty if p['uroven'] == 1]
    return punkty


# --- записываем ---------------------------------------------------------------
DIR_TELA = os.path.join(KOREN, 'src/content/toma', SLUG)
os.makedirs(DIR_TELA, exist_ok=True)
os.makedirs(os.path.join(KOREN, 'src/data/toma'), exist_ok=True)
for staryy in os.listdir(DIR_TELA):
    os.remove(os.path.join(DIR_TELA, staryy))

vsego_slov = 0
for st in stranicy:
    t = st['telo']
    if st['podnyat']:
        # заголовок раздела рисует каркас страницы, поэтому текст начинается
        # не с h3, а с h2 — иначе оглавление страницы окажется пустым
        t = re.sub(r'<(/?)h([3-6])([ >])',
                   lambda m: f'<{m.group(1)}h{int(m.group(2)) - 1}{m.group(3)}', t)
    t = pochistit(t)
    t = perepisat(t, st['slug'])
    st['toc'] = toc_iz(t)
    st['slov'] = slov_v(t)
    st['min'] = max(1, round(st['slov'] / 160))
    vsego_slov += st['slov']
    open(os.path.join(DIR_TELA, f'{st["slug"]}.html'), 'w', encoding='utf-8').write(t)

vv = perepisat(pochistit(vvedenie_telo), '')
open(os.path.join(DIR_TELA, 'vvedenie.html'), 'w', encoding='utf-8').write(vv)
vsego_slov += slov_v(vv)

ssylki = set(re.findall(r'href="(https?://[^"]+)"', telo))

meta = {
    'slug': SLUG,
    'title': BYLO.get('title') or nazvanie_ishodnika,
    'lede': BYLO.get('lede') or podzagolovok,
    'oblast': BYLO.get('oblast', ''),
    'data': BYLO.get('data', ''),
    'god': BYLO.get('god', ''),
    'versiya': versiya.group(1) if versiya else BYLO.get('versiya', ''),
    'kak_chitat': BYLO.get('kak_chitat', ''),
    'slov': vsego_slov,
    'min': max(1, round(vsego_slov / 160)),
    'ssylok': len(ssylki),
    'vvedenie': {'toc': toc_iz(vv), 'slov': slov_v(vv)},
    'chasti': [
        {
            'nomer': c['nomer'],
            'nazv': c['nazv'],
            'stranicy': [
                {'slug': st['slug'], 'label': st['label'], 'yakor': st['yakor'],
                 'slov': st['slov'], 'min': st['min'], 'toc': st['toc']}
                for st in c['stranicy']
            ],
        }
        for c in chasti
    ],
}

open(PUT_META, 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=False, indent=1))

# --- что вышло ----------------------------------------------------------------
bylo_str = {st['slug'] for c in BYLO.get('chasti', []) for st in c['stranicy']}
stalo_str = {st['slug'] for st in stranicy}
if bylo_str:
    for ushla in sorted(bylo_str - stalo_str):
        print(f'  ВНИМАНИЕ: страница /razbory/{SLUG}/{ushla}/ исчезла — адрес был в индексе')
    for novaya in sorted(stalo_str - bylo_str):
        print(f'  новая страница: /razbory/{SLUG}/{novaya}/')

if perepisat.bitye:
    print(f'  ВНИМАНИЕ: битых внутренних ссылок {len(perepisat.bitye)}:'
          f' {", ".join(sorted(set(perepisat.bitye))[:5])}')

for pole, chto in (('lede', 'подводка'), ('oblast', 'область'), ('data', 'дата'),
                   ('kak_chitat', 'текст плашки «Как читать»')):
    if not meta[pole]:
        print(f'  ВНИМАНИЕ: {chto} пуста — впишите руками в src/data/toma/{SLUG}.json,'
              f' следующий прогон её сохранит')

print(f'{SLUG}: частей {len(chasti)} · страниц {len(stranicy) + 1}'
      f' · слов {vsego_slov} · ссылок {len(ssylki)}'
      f' · таблиц {len(re.findall(r"<table", telo))}')
for c in chasti:
    print(f'  Часть {c["nomer"]}. {c["nazv"][:44]:46s} страниц {len(c["stranicy"]):2d}'
          f' · слов {sum(st["slov"] for st in c["stranicy"]):6d}')
