import { writable } from 'svelte/store';

async function getJSON(file: string) {
  const res = await fetch(`https://data.fieldmaps.io/${file}.json`);
  const data = await res.json();
  return data;
}

export const edgeMatched = writable([]);
export const adm0 = writable([]);
export const cod = writable([]);
export const geoboundaries = writable([]);
export const population = writable([]);

edgeMatched.set(await getJSON('edge-matched'));
adm0.set(await getJSON('adm0'));
cod.set(await getJSON('cod'));
geoboundaries.set(await getJSON('geoboundaries'));
population.set(await getJSON('population'));
