---
pageType: home

hero:
  name: AIO Sandbox
  text: 面向 AI Agents 的一体化安全开发沙盒
  tagline: |
    🌐 浏览器 | 💻 终端 | 📁 文件
    🔧 VSCode | 📊 Jupyter | 🤖 MCP
  actions:
    - theme: brand
      text: 快速开始
      link: /guide/start/introduction
    - theme: alt
      text: GitHub
      link: https://github.com/agent-infra/sandbox
  image:
    src: /aio-icon.png
    alt: AIO Sandbox Logo

features:
  - title: 统一环境
    details: 单一 Docker 容器，统一文件系统。浏览器下载的文件可立即在终端和 VSCode 中访问。
    icon: 🌐
  - title: 开箱即用
    details: 内置 VNC 浏览器、VSCode、Jupyter、文件和终端，通过 API/SDK 直接使用。
    icon: ⚡
  - title: 代码执行
    details: 完全隔离的 Python 与 Node.js 沙盒，安全运行代码。
    icon: 🔐
  - title: Agent-Ready
    details: 预配置 MCP Server，集成 Browser、File、Terminal、Markdown 和 Arxiv。即插即用，开箱即用支持 AI Agents。
    icon: 🤖
  - title: 开发者友好
    details: 云端 VSCode，持久化终端，服务端口转发（`${Port}-${domain}/` 或 `/proxy/${Port}），支持前端与后端应用即时预览。
    icon: 🔧
  - title: 面向生产环境
    details: 企业级 Docker 部署。轻量、可扩展。
    icon: 🚀
---
