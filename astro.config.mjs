// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

import { zakryt } from './src/data/sait.ts';
import { vidno } from './src/data/razdely.ts';

// Пути разделов, которые сейчас скрыты.
const SKRYTYE = Object.entries({
  '/muzyka/klipy/': vidno.muzyka_klipy,
  '/muzyka/koncerty/': vidno.muzyka_koncerty,
  '/muzyka/instrumentaly/': vidno.muzyka_instrumentaly,
  '/muzyka/stihi/': vidno.muzyka_stihi,
  '/muzyka/': vidno.muzyka,
  '/esse/': vidno.esse,
  '/razbory/': vidno.razbory,
  '/gaidy/': vidno.gaidy,
  '/foto/': vidno.foto,
  '/o-mne/': vidno.o_mne,
})
  .filter(([, otkryt]) => !otkryt)
  .map(([put]) => put);

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
              // Скрытый раздел в карту не попадает: карта — это приглашение
              // роботу, а раздел закрыт именно от него. Список путей тот же,
              // что в razdely.ts, но повторён здесь намеренно: конфиг Astro
              // читается до сборки, ему нужны голые строки, а не Astro.url.
              SKRYTYE.every((p) => !stranica.includes(p)) &&
              // страница поиска сама по себе пустая, индексировать нечего
              !stranica.includes('/poisk/'),
          }),
        ]),
  ],
});
