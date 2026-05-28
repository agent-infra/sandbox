# Skills

Skills are self-contained instruction and tool packages that can be registered in AIO Sandbox and discovered by an agent workflow.

## Skill Structure

A skill directory usually contains:

```text
my-skill/
  SKILL.md
  scripts/
  templates/
  requirements.txt
  package.json
```

`SKILL.md` is the entry point. It contains frontmatter metadata and Markdown instructions.

```md
---
name: report-writer
description: Create structured reports from source material.
---

# Report Writer

Use this skill when a task requires a structured report.
```

## Register A Skill

Register a skill directory that already exists inside the sandbox:

```bash
curl -X POST "http://localhost:8080/v1/skills/register" \
  -F "path=/home/gem/skills/report-writer"
```

Upload a zip archive and extract it under a destination directory:

```bash
curl -X POST "http://localhost:8080/v1/skills/register" \
  -F "file=@report-writer.zip" \
  -F "path=/home/gem/skills" \
  -F "name=report-writer"
```

## List Skills

```bash
curl "http://localhost:8080/v1/skills/metadatas"
```

## Read Skill Content

```bash
curl "http://localhost:8080/v1/skills/report-writer/content"
```

## Delete A Skill

```bash
curl -X DELETE "http://localhost:8080/v1/skills/report-writer"
```

## Best Practices

- Keep `description` short and action-oriented.
- Put heavy code in scripts, not in the Markdown instructions.
- Keep dependencies explicit and reproducible.
- Avoid embedding secrets in skill files.
