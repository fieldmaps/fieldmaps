export async function getJSON(file: string) {
  const res = await fetch(`https://data.fieldmaps.io/${file}.json`);
  const data = await res.json();
  return data;
}
