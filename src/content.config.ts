// Описание коллекций контента.
// Astro читает папку src/content/lenta, проверяет front matter каждого файла
// по схеме ниже и падает на сборке, если что-то не сходится.
// Это дешевле, чем ловить пустую дату на готовой странице.

import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const lenta = defineCollection({
  loader: glob({ base: './src/content/lenta', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    // Жанр решает, как запись показывается в ленте:
    // stihi и zametka — целиком, proza и esse — заголовком со ссылкой.
    kind: z.enum(['stihi', 'zametka', 'proza', 'esse']),
    source: z.string().optional(),
    description: z.string().optional(),
  }),
});

export const collections = { lenta };
