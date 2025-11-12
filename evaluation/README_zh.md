# AIO Sandbox 工具评测

[English](./README.md) | 简体中文

> 一个基于 aio-sandbox 的 MCP（模型上下文协议）工具和 AI 智能体能力的综合评测框架。

灵感来源：[Anthropic 的《writing-tools-for-agents》](https://www.anthropic.com/engineering/writing-tools-for-agents)


## 前置要求

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) 包管理器

## 安装

1. **克隆仓库**：
   ```bash
   git clone <repository-url>
   cd evaluation
   ```

2. **安装依赖**：
   ```bash
   # 只含 openai
   uv sync 
   # 含 langchain-opanai agent runtime
   uv sync --extra langchain-openai 
   ```

3. **配置环境**：
   ```bash
   cp .env.example .env
   ```

   编辑 `.env` 文件，填入你的凭据：
   ```env
   # OpenAI 配置
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_API_KEY=your-api-key
   OPENAI_MODEL_ID=gpt-4

   # MCP 服务器配置
   MCP_SERVER_URL=http://localhost:8080/mcp
   ```

## 使用方法

### 运行评测

```bash
# 运行所有评测
uv run aio-eval

# 运行特定评测
uv run aio-eval --eval ping
uv run aio-eval --eval basic
uv run aio-eval --eval browser

# 使用不同的 agent 运行时
uv run aio-eval --agent langchain --eval basic

# 列出所有可用的评测
uv run aio-eval --list

# 获取帮助
uv run aio-eval --help
```

你也可以直接运行主脚本：
```bash
uv run main.py --eval basic
python main.py --eval basic
```

查看 [CLI_USAGE.md](./CLI_USAGE.md) 了解详细的 CLI 使用文档。

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
├── main.py                 # ✨ CLI 入口点
├── pyproject.toml
├── aio_sandbox_eval/       # 评测框架
│   ├── cli/
│   │   └── utils.py        # CLI 辅助函数
│   ├── core/               # 核心逻辑
│   └── services/           # 服务层
└── agent_runtime/          # 自定义 agent 实现（自动发现）
├── dataset/                # 评测数据集
│   ├── evaluation_basic.xml
│   ├── evaluation_browser.xml
│   ├── evaluation_collaboration.xml
│   └── ...
└── result/                 # 评测报告（自动生成）
    └── YYYYMMDD/           # 基于日期的输出目录
        └── {agent}-{model}-{temp}/
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
   uv run aio-eval --eval mycategory
   ```

### 创建自定义 Agent 实现

该框架通过注册表模式支持自定义 agent 实现。你可以在不修改核心代码的情况下扩展评测框架。

**快速开始：**

```python
from aio_sandbox_eval.agent_runtime import BaseAgentLoop, AgentRegistry, AgentMessage

@AgentRegistry.register("my_custom_agent")
class MyCustomAgent(BaseAgentLoop):
    def __init__(self, mcp_session, model_name="gpt-4", **kwargs):
        super().__init__()
        self.mcp_session = mcp_session
        self.model_name = model_name
        # 你的自定义初始化

    async def run(self, prompt: str, tools: List[Dict[str, Any]]) -> List[AgentMessage]:
        # 你的 agent 逻辑
        pass

    async def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # 通过 MCP 执行工具
        result = await self.mcp_session.call_tool(tool_name, arguments=arguments)
        return result.model_dump() if hasattr(result, "model_dump") else result
```

**使用自定义 Agent：**

```bash
# 通过 CLI 的 --agent 参数
uv run aio-eval --agent my_custom_agent --eval basic

# 或者使用环境变量
export AGENT_TYPE=my_custom_agent
uv run aio-eval --eval basic
```


## 许可证

查看仓库根目录的 [LICENSE](../LICENSE) 文件。

## 参考资料

- [模型上下文协议（MCP）](https://modelcontextprotocol.io/)
- [Anthropic：为智能体编写工具](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [OpenAI API 文档](https://platform.openai.com/docs/)
