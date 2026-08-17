// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

import { zakryt } from './src/data/sait.ts';
import { pokazyvat as gaidyVidny } from './src/data/gaidy.ts';

export default defineConfig({
  site: 'https://glebmutovkin.ru',

  integrations: [
    // Карта сайта нужна, только когда сайт открыт поисковикам. Пока zakryt —
    // не собираем её вовсе, чтобы не оставлять на сервере готовый список
    // всех адресов.
    ...(zakryt
      ? []
      : [
          sitemap({
            filter: (stranica) =>
              // «Гайды» в карту не попадают, пока раздел скрыт: карта — это
              // приглашение роботу, а раздел закрыт именно от него.
              (gaidyVidny || !stranica.includes('/gaidy/')) &&
              // страница поиска сама по себе пустая, индексировать нечего
              !stranica.includes('/poisk/'),
          }),
        ]),
  ],
});
