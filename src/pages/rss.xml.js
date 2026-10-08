import rss from '@astrojs/rss';
import { getDiary, entryDate } from '../utils';

export async function GET(context) {
  const entries = await getDiary(); // newest first, original post order

  return rss({
    title: 'Jolly Follies: the diary',
    description: "Land's End to Sydney, overland, in a Land Rover called DINO. The travel diary, restored.",
    site: context.site,
    items: entries.map((e) => ({
      title: e.data.title,
      pubDate: e.data.date,
      link: `${import.meta.env.BASE_URL.replace(/\/$/, '')}/diary/${e.slug.replace(/^\d+-/, '')}/`,
    })),
    customData: `<language>en-gb</language>`,
  });
}
