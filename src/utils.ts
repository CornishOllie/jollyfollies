import { getCollection, type CollectionEntry } from 'astro:content';

export type DiaryEntry = CollectionEntry<'diary'>;

/** All non-draft diary entries, newest first. Sorted by the original post
 *  order (`order`), not `date`: a few dates mark when events happened, so
 *  date order would shuffle entries out of the sequence they were written. */
export async function getDiary(): Promise<DiaryEntry[]> {
  const entries = await getCollection('diary', ({ data }) => !data.draft);
  const key = (e: DiaryEntry) => e.data.order ?? Number.MAX_SAFE_INTEGER;
  return entries.sort((a, b) => key(b) - key(a) || b.data.date.getTime() - a.data.date.getTime());
}

/** All diary entries oldest first (chronological reading order). */
export async function getDiaryChrono(): Promise<DiaryEntry[]> {
  return (await getDiary()).slice().reverse();
}

/** Plain-text excerpt from a markdown body. */
export function excerpt(body: string, max = 150): string {
  const text = body
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')        // images
    .replace(/\*\(photo coming soon[^)]*\)\*/g, '')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')     // links -> text
    .replace(/[#*_>`-]/g, '')                    // md punctuation
    .replace(/\s+/g, ' ')
    .trim();
  if (text.length <= max) return text;
  return text.slice(0, max).replace(/\s+\S*$/, '') + '…';
}

export const fmtDate = (d: Date, precision: 'day' | 'month' = 'day') =>
  new Intl.DateTimeFormat('en-GB', precision === 'month'
    ? { month: 'long', year: 'numeric' }
    : { day: 'numeric', month: 'long', year: 'numeric' }).format(d);

/** An entry's date as shown to readers, respecting date_precision. */
export const entryDate = (e: DiaryEntry) => fmtDate(e.data.date, e.data.date_precision);
