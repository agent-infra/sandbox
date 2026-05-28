# Utilities

AIO Sandbox provides utility APIs for common agent tasks. The first public utility is content-to-Markdown conversion.

## Convert To Markdown

Use `/v1/util/convert_to_markdown` to convert a URI into Markdown text.

```bash
curl -X POST "http://localhost:8080/v1/util/convert_to_markdown" \
  -H "Content-Type: application/json" \
  -d '{
    "uri": "https://example.com"
  }'
```

The response can be passed to an agent, stored with the file API, or combined with browser automation results.

## Usage Patterns

- Convert public web pages before summarization.
- Convert downloaded documents after saving them to the sandbox filesystem.
- Normalize content before indexing or retrieval.

## Related

- [File Operations](/guide/basic/file)
- [Browser Automation](/guide/basic/browser)
- [Unified Code Execution](/guide/basic/code)

