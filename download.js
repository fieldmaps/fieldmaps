const fs = require('fs');
const https = require('https');

const urls = [
  'https://data.fieldmaps.io/edge-matched.json',
  'https://data.fieldmaps.io/adm0.json',
  'https://data.fieldmaps.io/cod.json',
  'https://data.fieldmaps.io/geoboundaries.json',
];
const data = `${__dirname}/data`;
if (!fs.existsSync(data)) fs.mkdirSync(data);

for (const url of urls) {
  https.get(url, res => {
    const path = `${data}/${url.substring(26)}`;
    const file = fs.createWriteStream(path);
    res.pipe(file);
    file.on('finish', () => file.close());
  });
}
