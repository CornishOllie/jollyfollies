import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  const entries = (await getCollection('diary', ({ data }) => !data.draft))
    .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());

  return rss({
    title: 'Jolly Follies: the diary',
    description: "Land's End to Sydney, overland, in a Land Rover called DINO. The travel diary, restored.",
    site: context.site,
    items: entries.map((e) => ({
      title: e.data.title,
      pubDate: e.data.date,
      link: `/diary/${e.slug.replace(/^\d+-/, '')}/`,
    })),
    customData: `<language>en-gb</language>`,
  });
}
