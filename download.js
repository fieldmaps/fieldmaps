import { existsSync, mkdirSync, createWriteStream } from 'fs';
import { get } from 'https';

const urls = [
  'https://data.fieldmaps.io/edge-matched.json',
  'https://data.fieldmaps.io/adm0.json',
  'https://data.fieldmaps.io/cod.json',
  'https://data.fieldmaps.io/geoboundaries.json',
  'https://data.fieldmaps.io/population.json',
];
const data = 'src/data';
if (!existsSync(data)) mkdirSync(data);

for (const url of urls) {
  get(url, (res) => {
    const path = `${data}/${url.substring(26)}`;
    const file = createWriteStream(path);
    res.pipe(file);
    file.on('finish', () => file.close());
  });
}
