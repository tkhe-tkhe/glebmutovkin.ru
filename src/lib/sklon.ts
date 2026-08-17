// Окончание существительного при числе: 1 текст, 2 текста, 5 текстов.
// Нужно потому, что счётчики на сайте живые: Глеб прячет тексты меткой
// [скрыто] в teksty-pesen.txt, и число меняется от правки к правке.
//
// formy — три формы подряд: для 1, для 2–4, для 5 и больше.
export function sklon(n: number, formy: [string, string, string]) {
  const a = Math.abs(n) % 100;
  const b = a % 10;
  if (a > 10 && a < 20) return formy[2];
  if (b > 1 && b < 5) return formy[1];
  if (b === 1) return formy[0];
  return formy[2];
}

export const TEKST: [string, string, string] = ['текст', 'текста', 'текстов'];
export const ZAPIS: [string, string, string] = ['запись', 'записи', 'записей'];
export const STROKA: [string, string, string] = ['строка', 'строки', 'строк'];
