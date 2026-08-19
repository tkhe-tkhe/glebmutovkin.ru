#!/usr/bin/env python3
"""Перегон teksty-pesen.txt -> src/data/stihi.json.

Источник правды — other/teksty-pesen.txt. Здесь только механика:

  === <номер> <Название> [метки]   начинает текст
  пустая строка внутри текста      граница строфы
  [скрыто]                         текст не попадает в JSON вообще
  [без названия]                   заголовок не выводится, в оглавлении «…»

Номер n закреплён за текстом навсегда. От него зависят slug и привязка
к клипам и концертам (поле pesnya), поэтому и slug, и pesnya берутся
из старого stihi.json по номеру, а не пересчитываются.

Ударение в файле ставится обратной кавычкой после ударной гласной
(«во`рота»), на сайт идёт комбинирующим акутом U+0301 («во́рота»).

    python3 tools/stihi.py <путь к teksty-pesen.txt>
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
VYHOD = KOREN / 'src' / 'data' / 'stihi.json'

# Транслитерация для slug у новых текстов. У существующих slug берётся
# из старого файла — переименование порвало бы якоря и ссылки из клипов.
TABLICA = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def sdelat_slug(nazvanie: str, n: int) -> str:
    s = ''.join(TABLICA.get(c, c) for c in nazvanie.lower())
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s or f'tekst-{n}'


def udarenie(s: str) -> str:
    """«во`рота» -> «во́рота»: обратная кавычка после гласной = акут над ней."""
    return re.sub(r'([аеёиоуыэюяАЕЁИОУЫЭЮЯ])`', lambda m: m.group(1) + '́', s)


def razobrat(tekst: str):
    bloki = re.split(r'^=== ', tekst, flags=re.M)[1:]
    for blok in bloki:
        zagolovok, _, telo = blok.partition('\n')
        m = re.match(r'(\d+)\s*(.*)$', zagolovok.strip())
        if not m:
            print(f'ВНИМАНИЕ: не разобрал строку === {zagolovok!r}')
            continue
        n = int(m.group(1))
        hvost = m.group(2)
        skryt = '[скрыто]' in hvost
        bez = '[без названия]' in hvost
        title = hvost.replace('[скрыто]', '').replace('[без названия]', '').strip()

        strofy = []
        for kusok in re.split(r'\n\s*\n', telo.strip()):
            stroki = [udarenie(l.rstrip()) for l in kusok.split('\n') if l.strip()]
            if stroki:
                strofy.append(stroki)

        yield {
            'n': n, 'title': title, 'bez_nazvaniya': bez,
            'skryt': skryt, 'strofy': strofy,
        }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    put = Path(sys.argv[1])
    syroy = put.read_text(encoding='utf-8-sig').replace('\r\n', '\n')

    staroe = json.loads(VYHOD.read_text(encoding='utf-8'))
    bylo = {t['n']: t for t in staroe['teksty']}

    teksty, skryto = [], 0
    for t in razobrat(syroy):
        if t['skryt']:
            skryto += 1
            continue
        prezhde = bylo.get(t['n'])
        if prezhde is None:
            print(f'НОВЫЙ текст n={t["n"]} «{t["title"]}» — slug сгенерирован')
        title = t['title'] or (prezhde['title'] if prezhde else f'Текст {t["n"]}')
        teksty.append({
            'n': t['n'],
            'slug': prezhde['slug'] if prezhde else sdelat_slug(title, t['n']),
            'title': title,
            'bez_nazvaniya': t['bez_nazvaniya'],
            'strofy': t['strofy'],
            'strok': sum(len(s) for s in t['strofy']),
            'pesnya': prezhde['pesnya'] if prezhde else [],
        })

    slugi = [t['slug'] for t in teksty]
    for s in set(slugi):
        if slugi.count(s) > 1:
            print(f'ВНИМАНИЕ: slug «{s}» встречается {slugi.count(s)} раз')

    ushli = sorted(set(bylo) - {t['n'] for t in teksty})
    for n in ushli:
        if bylo[n]['pesnya']:
            print(f'ВНИМАНИЕ: n={n} «{bylo[n]["title"]}» скрыт, но привязан '
                  f'к записи — у видео пропадёт кнопка «Текст»')

    staroe['teksty'] = teksty
    VYHOD.write_text(
        json.dumps(staroe, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    print(f'Готово: {len(teksty)} текстов в JSON, {skryto} скрыто, '
          f'{sum(t["strok"] for t in teksty)} строк.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
