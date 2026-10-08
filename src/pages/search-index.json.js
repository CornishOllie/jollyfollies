import { getDiary, entryDate } from '../utils';

// A small static search index over the diary, fetched by /search/.
export async function GET() {
  const entries = await getDiary(); // newest first, original post order

  const index = entries.map((e) => ({
    title: e.data.title,
    url: `/diary/${e.slug.replace(/^\d+-/, '')}/`,
    date: e.data.date.toISOString().slice(0, 10),
    dateLabel: entryDate(e),
    text: e.body
      .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
      .replace(/\*\(photo coming soon[^)]*\)\*/g, '')
      .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
      .replace(/[#*_>`]/g, '')
      .replace(/\s+/g, ' ')
      .trim(),
  }));

  return new Response(JSON.stringify(index), {
    headers: { 'Content-Type': 'application/json' },
  });
}
