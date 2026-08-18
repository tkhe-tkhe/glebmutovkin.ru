// Файлы гайда для скачивания.
//
// Лежат в public/files/gaidy/<slug>.<расширение> и попадают на сервер как есть.
// Размер не записан руками, а читается с диска на сборке: файл поменялся —
// подпись под кнопкой поменялась сама. Зашитое число разошлось бы с файлом
// молча, и никто бы этого не заметил.
//
// Формата, которого нет на диске, в списке не будет: кнопка не появится,
// сборка не упадёт. Так гайд можно выложить хоть с одним PDF.

import { statSync } from 'node:fs';
import { join } from 'node:path';

// Порядок кнопок. PDF первым: он нужен чаще всего — открыть в студии
// и читать без интернета.
const FORMATY = [
  { rasshirenie: 'pdf', label: 'PDF', chto: 'читать и печатать' },
  { rasshirenie: 'docx', label: 'DOCX', chto: 'править под себя' },
  { rasshirenie: 'epub', label: 'EPUB', chto: 'телефон и ридер' },
  { rasshirenie: 'html', label: 'HTML', chto: 'одним файлом в браузер' },
] as const;

export interface Fail {
  url: string;
  label: string;
  chto: string;
  ves: string;
}

// 1 048 576 → «1,0 МБ». Разделитель — запятая: это русский текст, а не код.
function ves(baytov: number): string {
  const mb = baytov / 1024 / 1024;
  if (mb >= 1) return `${mb.toFixed(1).replace('.', ',')} МБ`;
  return `${Math.round(baytov / 1024)} КБ`;
}

export function faily(slug: string): Fail[] {
  const out: Fail[] = [];

  for (const f of FORMATY) {
    const otn = `files/gaidy/${slug}.${f.rasshirenie}`;
    try {
      // process.cwd() на сборке — корень проекта, там же лежит public/
      const st = statSync(join(process.cwd(), 'public', otn));
      if (!st.isFile()) continue;
      out.push({ url: `/${otn}`, label: f.label, chto: f.chto, ves: ves(st.size) });
    } catch {
      // файла нет — формат просто не показываем
    }
  }

  return out;
}
