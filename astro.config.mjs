// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Live at the custom domain jollyfollies.co.uk (public/CNAME), so no base path.
// The 2009 replica (../jollyfollies-replica) is built into /classic by the deploy script.
export default defineConfig({
  site: 'https://jollyfollies.co.uk',
  integrations: [sitemap()],
  build: { format: 'directory' },
});
