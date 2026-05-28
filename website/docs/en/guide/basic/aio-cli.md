# AIO CLI

The `aio` command-line tool wraps common AIO Sandbox APIs for terminal and agent workflows. It is available inside the sandbox container.

## Common Commands

```bash
# Navigate the browser
aio browser navigate https://example.com

# Take a page screenshot
aio browser screenshot -o /home/gem/page.png

# Take a desktop screenshot at the GUI layer
aio gui screenshot -o /home/gem/desktop.png

# List MCP servers
aio mcp list

# List registered Skills
aio skills list

# Show sandbox information
aio sandbox info
```

## Command Groups

| Group | Purpose |
| --- | --- |
| `browser` | Browser navigation and page automation |
| `gui` | Desktop-level screenshot and interaction |
| `sandbox` | Environment information |
| `skills` | Skill registration and inspection |
| `mcp` | MCP server and tool calls |

## Output

The CLI is designed for both people and agents:

- Human-readable output when used in a terminal.
- Structured JSON when used in scripts or pipelines.
- Explicit exit codes for failure handling.

## Configuration

Inside the container the CLI can target the local sandbox service automatically. When calling a remote sandbox, pass an API URL with `--api-url`.

## Related

- [Browser Automation](/guide/basic/browser)
- [Skills](/guide/basic/skills)
- [MCP](/guide/basic/mcp)
