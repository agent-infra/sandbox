# Skills

Skills 是可注册到 AIO Sandbox 的自包含指令和工具包，可被 Agent 工作流发现和使用。

## Skill 结构

一个 Skill 目录通常包含：

```text
my-skill/
  SKILL.md
  scripts/
  templates/
  requirements.txt
  package.json
```

`SKILL.md` 是入口文件，包含 frontmatter 元数据和 Markdown 指令。

```md
---
name: report-writer
description: Create structured reports from source material.
---

# Report Writer

Use this skill when a task requires a structured report.
```

## 注册 Skill

注册沙盒内已经存在的 Skill 目录：

```bash
curl -X POST "http://localhost:8080/v1/skills/register" \
  -F "path=/home/gem/skills/report-writer"
```

上传 zip 并解压到目标目录：

```bash
curl -X POST "http://localhost:8080/v1/skills/register" \
  -F "file=@report-writer.zip" \
  -F "path=/home/gem/skills" \
  -F "name=report-writer"
```

## 查询 Skills

```bash
curl "http://localhost:8080/v1/skills/metadatas"
```

## 读取 Skill 内容

```bash
curl "http://localhost:8080/v1/skills/report-writer/content"
```

## 删除 Skill

```bash
curl -X DELETE "http://localhost:8080/v1/skills/report-writer"
```

## 最佳实践

- `description` 保持简短，并说明触发场景。
- 大段代码放在脚本中，不要塞进 Markdown 指令。
- 依赖声明保持明确、可复现。
- 不要把密钥写入 Skill 文件。
