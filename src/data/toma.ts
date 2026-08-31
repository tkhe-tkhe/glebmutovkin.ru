// Типы тома — многостраничного разбора.
//
// Сами данные лежат в src/data/toma/<slug>.json и собираются конвейером
// tools/tom.py: он режет исходник на страницы, считает слова и строит
// оглавление каждой страницы. Здесь только описание формы этих данных,
// чтобы каркасы и маршруты не разъехались с конвейером молча.
//
// Поля, которых в исходнике нет — title, lede, oblast, data, kak_chitat, —
// вписываются руками в JSON; следующий прогон скрипта их сохраняет.

export interface TocPunkt {
  href: string;
  label: string;
  /** 1 — раздел (h2), 2 — подраздел (h3) */
  uroven: number;
}

export interface TomStranica {
  slug: string;
  label: string;
  /** якорь заголовка из исходника: на него ссылаются с соседних страниц */
  yakor: string;
  slov: number;
  min: number;
  toc: TocPunkt[];
}

export interface TomChast {
  nomer: string;
  nazv: string;
  stranicy: TomStranica[];
}

export interface TomMeta {
  slug: string;
  title: string;
  lede: string;
  oblast: string;
  data: string;
  god: string;
  versiya: string;
  /** текст плашки «Как читать этот том»; {n} подставляется числом ссылок */
  kak_chitat: string;
  slov: number;
  min: number;
  ssylok: number;
  vvedenie: { toc: TocPunkt[]; slov: number };
  chasti: TomChast[];
}
