// Видимость разделов: один переключатель на раздел.
//
// Правило одно на весь сайт — то же, по которому с 16 августа 2026 жили
// «Гайды», а с 24 августа так же живут остальные разделы:
//
//   true   — пункт стоит в меню, страницы попадают в поиск по сайту,
//            в карту сайта и открыты поисковикам.
//   false  — пункта в меню нет, из поиска по сайту раздел убран, в карту
//            сайта не попадает, на страницах noindex. Сами страницы при этом
//            собираются и открываются по прямой ссылке. Так можно дать ссылку
//            на конкретный материал, не открывая раздел целиком.
//
// Ленты в списке нет намеренно: это главная страница сайта, скрыть её значит
// убрать сайт. Для этого есть отдельный флаг zakryt в sait.json.
//
// В robots.txt скрытые разделы намеренно НЕ прописываются: строка Disallow
// объявила бы адрес каждому, кто откроет файл, — ровно обратное тому, зачем
// раздел скрыт.
//
// Чего этот переключатель НЕ делает: он прячет витрину раздела, а не его
// содержимое. Скрытые «Эссе и проза» убирают список, но сами тексты остаются
// в ленте и на /zapis/<id> — у каждого текста одно каноническое место,
// и оно в ленте. Решение Глеба от 24 августа 2026.
//
// То же и внутри музыки: скрытая полка «Тексты песен» убирает собрание,
// но кнопка «Текст» у клипа, концерта и студийной записи остаётся. Слова
// у видео — часть самой записи, а не ссылка на собрание. Решение Глеба.
//
// Значения лежат в razdely.json — это формат, который читает админка.
// Здесь остались пояснения: JSON комментариев не держит. Поля вроде
// "_comment" в этот файл класть нельзя: админка сохраняет ровно те поля,
// что описаны в её форме, и лишнее сотрёт при первой же правке.

import dannye from './razdely.json';

export type Razdel =
  | 'muzyka'
  | 'muzyka_klipy'
  | 'muzyka_koncerty'
  | 'muzyka_instrumentaly'
  | 'muzyka_stihi'
  | 'esse'
  | 'razbory'
  | 'gaidy'
  | 'foto'
  | 'o_mne';

// У музыки четыре полки, и каждая гасится отдельно. Полка внутри скрытого
// раздела скрыта в любом случае — иначе «Музыка» выключена, а концерты
// остались бы в поиске и в карте сайта.
const vnutriMuzyki = (svoy: boolean) => dannye.muzyka && svoy;

export const vidno: Record<Razdel, boolean> = {
  muzyka: dannye.muzyka,
  muzyka_klipy: vnutriMuzyki(dannye.muzyka_klipy),
  muzyka_koncerty: vnutriMuzyki(dannye.muzyka_koncerty),
  muzyka_instrumentaly: vnutriMuzyki(dannye.muzyka_instrumentaly),
  muzyka_stihi: vnutriMuzyki(dannye.muzyka_stihi),
  esse: dannye.esse,
  razbory: dannye.razbory,
  gaidy: dannye.gaidy,
  foto: dannye.foto,
  o_mne: dannye.o_mne,
};

// Начало пути -> раздел. Порядок здесь значим: полки музыки лежат внутри
// /muzyka/, и проверять их надо раньше самого раздела — иначе /muzyka/klipy/
// совпадёт с общим префиксом и своего переключателя не увидит.
const PUTI: [string, Razdel][] = [
  ['/muzyka/klipy/', 'muzyka_klipy'],
  ['/muzyka/koncerty/', 'muzyka_koncerty'],
  ['/muzyka/instrumentaly/', 'muzyka_instrumentaly'],
  ['/muzyka/stihi/', 'muzyka_stihi'],
  ['/muzyka/', 'muzyka'],
  ['/esse/', 'esse'],
  ['/razbory/', 'razbory'],
  ['/gaidy/', 'gaidy'],
  ['/foto/', 'foto'],
  ['/o-mne/', 'o_mne'],
];

/** Какому разделу принадлежит адрес. null — лента или служебная страница. */
export function razdelPoPuti(put: string): Razdel | null {
  const nayden = PUTI.find(([prefiks]) => put.startsWith(prefiks));
  return nayden ? nayden[1] : null;
}

/** Скрыт ли раздел, которому принадлежит адрес. */
export function skryt(put: string): boolean {
  const r = razdelPoPuti(put);
  return r !== null && !vidno[r];
}
