# Display Recording

AIO Sandbox can record the full desktop display and save it as an MP4 file. This captures browser UI, multiple tabs, popups, terminal windows, and any visible desktop activity.

Use display recording when you need a complete visual audit trail. For page-only browser content, use browser page recording instead.

## Start Recording

```bash
curl -X POST "http://localhost:8080/v1/display/record" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "start",
    "save_path": "/home/gem/recordings/session.mp4"
  }'
```

## Check Status

```bash
curl -X POST "http://localhost:8080/v1/display/record" \
  -H "Content-Type: application/json" \
  -d '{"action": "status"}'
```

## Stop Recording

```bash
curl -X POST "http://localhost:8080/v1/display/record" \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'
```

## Tips

- Store recordings under the workspace or another known directory so they can be retrieved with the file API.
- Stop recording before deleting the container when you need a complete playable file.
- Use short recordings for debugging and acceptance tests to keep file size manageable.

## Related

- [Browser Automation](/guide/basic/browser)
- [File Operations](/guide/basic/file)
