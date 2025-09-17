---
pageType: home

hero:
  name: AIO Sandbox
  text: All-in-One Sandbox for AI Agents
  tagline: |
    🌐 Browser | 💻 Terminal | 📁 File
    🔧 VSCode | 📊 Jupyter | 🤖 MCP
  actions:
    - theme: brand
      text: Get Started
      link: /guide/start/introduction
    - theme: alt
      text: View on GitHub
      link: https://github.com/agent-infra/sandbox
  image:
    src: /aio-icon.png
    alt: AIO Sandbox Logo

features:
  - title: Unified Environment
    details: One Docker container, shared filesystem. Browser downloads instantly available in Terminal and Code.
    icon: 🌐
  - title: Instant Development
    details: VNC browser, VSCode, Jupyter, Terminal. Access via ${port}-${domain} or /proxy paths.
    icon: ⚡
  - title: Secure Execution
    details: Isolated Python and Node.js sandboxes. Safe code execution without system risks.
    icon: 🔐
  - title: Agent-Ready
    details: MCP Hub at /mcp with Browser, File, Terminal, Markitdown, Arxiv. Plug and play for AI agents.
    icon: 🤖
  - title: Developer Friendly
    details: Cloud VSCode, persistent terminals, smart port forwarding, frontend/backend preview.
    icon: 🔧
  - title: Production Ready
    details: Enterprise-grade Docker deployment. Lightweight, scalable, battle-tested.
    icon: 🚀
---

## Quick Start

Get AIO Sandbox running in under 30 seconds:

```bash
# 🚀 Start the sandbox (International)
docker run --rm -it -p 8080:8080 ghcr.io/agent-infra/sandbox:v1

# 🇨🇳 For users in mainland China
docker run --rm -it -p 8080:8080 enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:v1
```

**Access your sandbox environment:**
- 📖 **Documentation**: http://localhost:8080/v1/docs
- 🌐 **VNC Browser**: http://localhost:8080/vnc/index.html?autoconnect=true
- 💻 **VSCode Server**: http://localhost:8080/code-server/
- 🤖 **MCP Services**: http://localhost:8080/mcp

## Why Choose AIO Sandbox?

**Perfect for AI agents, developers, and automation workflows:**

✅ **Unified File System** - Files downloaded in browser are instantly available in Shell/File operations
✅ **Multiple Interfaces** - VNC, VSCode, Jupyter, and Terminal in one unified environment
✅ **Secure Execution** - Sandboxed Python and Node.js execution with safety guarantees
✅ **Zero Configuration** - Pre-configured MCP servers and development tools ready to use
✅ **Flexible Deployment** - Single Docker container, cloud-native, scales with your needs

## What's Inside

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 Browser + VNC                        │
├─────────────────────────────────────────────────────────────┤
│  💻 VSCode Server  │  🐚 Shell Terminal  │  📁 File Ops   │
├─────────────────────────────────────────────────────────────┤
│              🔗 MCP Hub + 🔒 Sandbox Fusion               │
├─────────────────────────────────────────────────────────────┤
│         🚀 Preview Proxy + 📊 Service Monitoring          │
└─────────────────────────────────────────────────────────────┘
```

Ready to revolutionize your AI development workflow?

🚀 [**Get Started Now →**](/guide/start/introduction) | 📚 [**View Examples →**](/examples/) | 🔧 [**API Docs →**](/api/)
