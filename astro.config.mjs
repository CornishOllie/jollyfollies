// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Set this to your final URL. For GitHub Pages project sites use:
//   site: 'https://<user>.github.io', base: '/jollyfollies'
// For a custom domain (jollyfollies.com) use the bare domain and drop `base`.
export default defineConfig({
  site: 'https://jollyfollies.com',
  integrations: [sitemap()],
  build: { format: 'directory' },
});
