import { defineCollection, z } from 'astro:content';

// The diary: one Markdown file per entry. Add a new entry by dropping a file
// in src/content/diary/ with this front matter — see README.
const diary = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    order: z.number().optional(),
    original_url: z.string().optional(),
    location: z.string().optional(),
    cover: z.string().optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { diary };
