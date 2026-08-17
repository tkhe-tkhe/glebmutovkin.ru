// robots.txt собирается, а не лежит файлом: его содержимое зависит от флага
// zakryt в src/data/sait.ts.
//
// Раздел «Гайды» здесь намеренно НЕ упоминается. Строка Disallow: /gaidy/
// объявила бы адрес каждому, кто откроет robots.txt, — то есть сделала бы
// ровно обратное тому, зачем раздел скрыт. Его закрывает noindex на страницах.

import type { APIRoute } from 'astro';
import { zakryt, adres } from '../data/sait';

export const GET: APIRoute = () => {
  const telo = zakryt
    ? `User-agent: *\nDisallow: /\n`
    : `User-agent: *\nAllow: /\nDisallow: /poisk/\n\nSitemap: ${adres}/sitemap-index.xml\n`;

  return new Response(telo, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
