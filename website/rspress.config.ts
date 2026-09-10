import * as path from 'node:path';
import { pluginSass } from '@rsbuild/plugin-sass';
import { pluginSvgr } from '@rsbuild/plugin-svgr';
import { defineConfig } from '@rspress/core';
import { pluginLlms } from '@rspress/plugin-llms';
import { pluginSitemap } from '@rspress/plugin-sitemap';
import {
  transformerNotationDiff,
  transformerNotationErrorLevel,
  transformerNotationFocus,
  transformerNotationHighlight,
} from '@shikijs/transformers';
import { pluginGoogleAnalytics } from 'rsbuild-plugin-google-analytics';
import { pluginOpenGraph } from 'rsbuild-plugin-open-graph';
import { pluginFontOpenSans } from 'rspress-plugin-font-open-sans';

const siteUrl = 'https://sandbox.agent-infra.com';

// The llms plugin's own mdxToMd drops import lines and unwraps JSX, but it
// glues the v1/v2 route spans together. This does the same and separates
// adjacent inline components with " / ".
function mdxToPlainMarkdown() {
  const isJsx = (n: any) => n.type === 'mdxJsxFlowElement' || n.type === 'mdxJsxTextElement';
  const walk = (node: any) => {
    if (!Array.isArray(node.children)) return;
    const out: any[] = [];
    let prevJsx = false;
    for (const child of node.children) {
      if (child.type === 'mdxjsEsm') continue;
      if (child.type === 'blockquote') keepAlertMarker(child);
      if (isJsx(child)) {
        walk(child);
        if (prevJsx && child.type === 'mdxJsxTextElement') out.push({ type: 'text', value: ' / ' });
        out.push(...(child.children ?? []));
        prevJsx = true;
        continue;
      }
      prevJsx = false;
      walk(child);
      out.push(child);
    }
    node.children = out;
  };
  return (tree: any) => walk(tree);
}

// remark-stringify would escape "> [!TIP]" to "> \[!TIP]".
function keepAlertMarker(blockquote: any) {
  const paragraph = blockquote.children?.[0];
  const text = paragraph?.children?.[0];
  const marker = text?.type === 'text' && /^\[!\w+\]/.exec(text.value);
  if (!marker) return;
  text.value = text.value.slice(marker[0].length);
  paragraph.children.unshift({ type: 'html', value: marker[0] });
}

const llmsMdFiles = { mdxToMd: false, remarkPlugins: [mdxToPlainMarkdown] };

export default defineConfig({
  root: path.join(__dirname, 'docs'),
  lang: 'en',
  title: 'AIO Sandbox',
  description:
    'All-in-One Agent Sandbox Environment - Browser, Shell, File, VSCode Server, and MCP Hub in One Container',
  icon: '/aio-icon.png',
  logo: {
    dark: '/aio-icon.png',
    light: '/aio-icon.png',
  },
  themeDir: path.join(__dirname, 'theme'),
  route: {
    cleanUrls: true,
  },
  markdown: {
    shiki: {
      langAlias: {
        Bash: 'shellscript',
        Shell: 'shellscript',
        Dockerfile: 'docker',
        Python: 'python',
      },
      langs: ['shellscript', 'docker', 'python'],
      transformers: [
        transformerNotationDiff(),
        transformerNotationErrorLevel(),
        transformerNotationHighlight(),
        transformerNotationFocus(),
      ],
    },
    link: {
      checkDeadLinks: false,
    },
  },
  plugins: [
    pluginFontOpenSans(),
    pluginSitemap({
      siteUrl,
    }),
    // One entry per locale: a single options object only covers the default
    // language, so zh pages had no .md files and "Copy Markdown" fetched the 404 page.
    pluginLlms([
      { mdFiles: llmsMdFiles },
      {
        mdFiles: llmsMdFiles,
        llmsTxt: { name: 'zh/llms.txt' },
        llmsFullTxt: { name: 'zh/llms-full.txt' },
        include: ({ page }) => page.lang === 'zh',
      },
    ]),
  ],
  base: process.env.BASE_URL ?? '/',
  outDir: 'doc_build',
  builderConfig: {
    html: {
      template: 'public/index.html',
    },
    tools: {
      // Fast refresh only for project files. The refresh runtime is appended
      // to every compiled module and calls Promise.resolve(); a dependency
      // that exports its own `Promise` (@scalar/typebox) then breaks in dev.
      bundlerChain(chain, { CHAIN_ID }) {
        const refresh = chain.plugins.get(CHAIN_ID.PLUGIN.REACT_FAST_REFRESH);
        if (refresh) {
          refresh.tap(([options]) => [
            { ...options, exclude: [...(options.exclude ?? []), /[\\/]node_modules[\\/]/] },
          ]);
        }
      },
    },
    plugins: [
      pluginSass(),
      pluginSvgr({ svgrOptions: { exportType: 'default' } }),
      pluginGoogleAnalytics({ id: 'G-VDPJE6PYSN' }),
      pluginOpenGraph({
        url: siteUrl,
        image: 'https://rspress.rs/og-image.png',
        description: 'Rsbuild based static site generator',
        twitter: {
          site: '@rspack_dev',
          card: 'summary_large_image',
        },
      }),
    ],
  },
  locales: [
    {
      lang: 'en',
      label: 'English',
      title: 'AIO Sandbox',
      description: 'All-in-One Environment for AI Agents',
    },
    {
      lang: 'zh',
      label: '简体中文',
      title: 'AIO Sandbox',
      description: '面向 AI Agents 的一体化沙盒环境',
    },
  ],
  themeConfig: {
    // hideNavbar: 'auto',
    socialLinks: [
      {
        icon: 'github',
        mode: 'link',
        content: 'https://github.com/agent-infra/sandbox',
      },
    ],
    footer: {
      message: 'Built with ❤️ for AI Agents · AIO Sandbox © 2026',
    },
    locales: [
      {
        lang: 'en',
        label: 'English',
        editLink: {
          docRepoBaseUrl:
            'https://github.com/agent-infra/sandbox/tree/main/website/docs',
          text: '📝 Edit this page on GitHub',
        },
        searchPlaceholderText: 'Search',
        searchPanelCancelText: 'Cancel',
        searchNoResultsText: 'No matching results',
        searchSuggestedQueryText: 'Try searching for different keywords',
      },
      {
        lang: 'zh',
        label: '简体中文',
        editLink: {
          docRepoBaseUrl:
            'https://github.com/agent-infra/sandbox/tree/main/website/docs',
          text: '📝 在 GitHub 上编辑此页',
        },
        searchPlaceholderText: '搜索',
        searchPanelCancelText: '取消',
        searchNoResultsText: '未找到匹配的结果',
        searchSuggestedQueryText: '尝试搜索其他关键词',
        overview: {
          filterNameText: '过滤',
          filterPlaceholderText: '输入关键词',
          filterNoResultText: '未找到匹配的 API',
        },
      },
    ],
  },
  languageParity: {
    enabled: false,
    include: [],
    exclude: [],
  },
});
