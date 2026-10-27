// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import { site } from './site.config.ts';

// PREVIEW=1 → jednosouborový build (fonty i JS vložené do HTML) pro náhled jako Claude artifact
const preview = process.env.PREVIEW === '1';

export default defineConfig({
  site: site.url,
  ...(preview && { outDir: './dist-preview' }),
  trailingSlash: 'never',
  build: { format: 'file', inlineStylesheets: 'always' },
  integrations: [sitemap()],
  vite: {
    plugins: [tailwindcss()],
    ...(preview && { build: { assetsInlineLimit: 10_000_000 } }),
  },
});
