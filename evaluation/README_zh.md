# AIO Sandbox 工具评测

[English](./README.md) | 简体中文

> 一个基于 aio-sandbox 的 MCP（模型上下文协议）工具和 AI 智能体能力的综合评测框架。

来源：[Anthropic 的《为智能体编写工具》](https://www.anthropic.com/engineering/writing-tools-for-agents)


## 前置要求

- Python >= 3.13
- [uv](https://github.com/astral-sh/uv) 包管理器

## 安装

1. **克隆仓库**：
   ```bash
   git clone <repository-url>
   cd evaluation
   ```

2. **安装依赖**：
   ```bash
   uv sync
   ```

3. **配置环境**：
   ```bash
   cp .env.example .env
   ```

   编辑 `.env` 文件，填入你的凭据：
   ```env
   # Azure OpenAI 配置
   OPENAI_BASE_URL=https://your-endpoint.openai.azure.com
   OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_DEPLOYMENT=gpt-4
   AZURE_OPENAI_API_VERSION=2024-02-15-preview

   # MCP 服务器配置
   MCP_SERVER_URL=http://localhost:8080/mcp

   # 可选：并发配置
   MAX_CONCURRENT_TASKS=5
   ```

## 使用方法

### 运行所有评测

顺序运行所有评测文件：

```bash
uv run main.py
```

### 运行特定评测

运行特定评测类别：

```bash
uv run main.py --eval basic
uv run main.py --eval browser
uv run main.py --eval collaboration
uv run main.py --eval workflow
```

### 可用的评测类别

| 类别 | 描述 |
|------|------|
| `ping` | 基础连通性测试 |
| `basic` | 单工具能力测试（文件操作、代码执行、Shell） |
| `browser` | 浏览器自动化基础（导航、DOM、表单） |
| `browser_advanced` | 高级浏览器交互（点击、悬停、键盘操作） |
| `code_advanced` | 高级代码执行（异步、错误处理、数据结构） |
| `collaboration` | 多工具协作流程（文件+代码、浏览器+文件） |
| `editor` | 文本编辑器操作（查看、创建、替换、插入、撤销） |
| `packages` | 包管理（Python、Node.js） |
| `util` | 实用工具（Markdown 转换） |
| `error` | 错误处理测试 |
| `workflow` | 真实场景（代码审查、数据管道、爬虫html展示） |
| `nextjs` | Next.js 项目启动 |

## 项目结构

```
evaluation/
├── main.py                 # 主入口和评测编排
├── agent_loop.py          # 智能体循环实现（Azure OpenAI 等）
├── dataset_parser.py      # XML 数据集解析器
├── .env.example           # 环境配置模板
├── pyproject.toml         # 项目依赖
├── dataset/               # 评测数据集
│   ├── evaluation_basic.xml
│   ├── evaluation_browser.xml
│   ├── evaluation_collaboration.xml
│   └── ...
└── result/                # 评测报告（自动生成）
    └── YYYYMMDD/          # 基于日期的输出目录
        └── evaluation_*.md
```

## 扩展框架

### 添加新的评测类别

1. 在 `dataset/` 目录创建 XML 文件：
   ```
   dataset/evaluation_mycategory.xml
   ```

2. 运行：
   ```bash
   uv run main.py --eval mycategory
   ```



## 贡献

欢迎贡献！请：

1. Fork 仓库
2. 创建功能分支
3. 为新功能添加测试
4. 确保所有测试通过
5. 提交 Pull Request

## 许可证

查看仓库根目录的 [LICENSE](../LICENSE) 文件。

## 参考资料

- [模型上下文协议（MCP）](https://modelcontextprotocol.io/)
- [Anthropic：为智能体编写工具](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Azure OpenAI 文档](https://learn.microsoft.com/zh-cn/azure/ai-services/openai/)
