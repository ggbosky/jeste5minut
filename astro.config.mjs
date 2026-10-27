// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import { site } from './site.config.ts';

export default defineConfig({
  site: site.url,
  trailingSlash: 'never',
  build: { format: 'file', inlineStylesheets: 'always' },
  integrations: [sitemap()],
  vite: { plugins: [tailwindcss()] },
});
