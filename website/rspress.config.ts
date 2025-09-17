import * as path from 'node:path';
import { pluginLlms } from '@rspress/plugin-llms';
import { defineConfig } from '@rspress/core';

export default defineConfig({
  lang: 'en',
  root: path.join(__dirname, 'docs'),
  title: 'AIO Sandbox',
  description:
    'All-in-One Agent Sandbox Environment - Browser, Shell, File, VSCode Server, and MCP Hub in One Container',
  icon: '/aio-icon.png',
  logo: {
    dark: '/aio-icon.png',
    light: '/aio-icon.png',
  },
  route: {
    cleanUrls: true,
  },
  plugins: [pluginLlms()],
  base: process.env.BASE_URL ?? '/',
  outDir: 'doc_build',
  builderConfig: {},
  locales: [
    {
      lang: 'en',
      label: 'English',
      title: 'Rspress',
      description: 'Static Site Generator',
    },
    {
      lang: 'zh',
      label: '简体中文',
      title: 'Rspress',
      description: '静态网站生成器',
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
      message: 'Built with ❤️ for AI Agents · AIO Sandbox © 2025',
    },
    locales: [
      {
        lang: 'zh',
        label: '简体中文',
        editLink: {
          docRepoBaseUrl:
            'https://github.com/agent-infra/sandbox/tree/main/site/docs',
          text: '📝 在 GitHub 上编辑此页',
        },
        overview: {
          filterNameText: '过滤',
          filterPlaceholderText: '输入关键词',
          filterNoResultText: '未找到匹配的 API',
        },
      },
      {
        lang: 'en',
        label: 'English',
        editLink: {
          docRepoBaseUrl:
            'https://github.com/agent-infra/sandbox/tree/main/site/docs',
          text: '📝 Edit this page on GitHub',
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
