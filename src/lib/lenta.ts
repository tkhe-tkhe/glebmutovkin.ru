// Мелкие помощники ленты. Вынесены отдельно, чтобы не дублировать
// в главной странице и на странице отдельной записи.

export const KIND_LABEL: Record<string, string> = {
  stihi: 'Стихи',
  zametka: 'Заметка',
  proza: 'Проза',
  esse: 'Эссе',
};

// Жанры, которые показываются в ленте целиком.
export const FULL_KINDS = ['stihi', 'zametka'];

// Дата моноширинным, ровным столбиком: 02.08.2026
export function formatDate(d: Date): string {
  const p = (n: number) => String(n).padStart(2, '0');
  return `${p(d.getDate())}.${p(d.getMonth() + 1)}.${d.getFullYear()}`;
}

// Первые слова текста для подводки под заголовком.
// Markdown-разметку выбрасываем: в подводке она только мешает.
export function excerpt(body: string, words = 28): string {
  const plain = body
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/[*_`>#]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
  const parts = plain.split(' ');
  return parts.length <= words ? plain : parts.slice(0, words).join(' ') + '…';
}
