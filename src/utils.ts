import { getCollection, type CollectionEntry } from 'astro:content';

export type DiaryEntry = CollectionEntry<'diary'>;

/** All non-draft diary entries, newest first. */
export async function getDiary(): Promise<DiaryEntry[]> {
  const entries = await getCollection('diary', ({ data }) => !data.draft);
  return entries.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
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

export const fmtDate = (d: Date) =>
  new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'long', year: 'numeric' }).format(d);
