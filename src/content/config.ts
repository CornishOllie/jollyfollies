import { defineCollection, z } from 'astro:content';

// The diary: one Markdown file per entry. Add a new entry by dropping a file
// in src/content/diary/ with this front matter — see README.
const diary = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    // 'month' when only the month is known: shown as "December 2006".
    date_precision: z.enum(['day', 'month']).default('day'),
    order: z.number().optional(),
    original_url: z.string().optional(),
    location: z.string().optional(),
    cover: z.string().optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { diary };
