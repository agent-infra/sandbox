# WebTerminal Integration

AIO Sandbox provides a built-in Web Terminal page and exposes a Shell WebSocket endpoint so you can embed a terminal in your own local web UI.

The examples below assume AIO Sandbox is running at `http://localhost:8080`.

## Built-In Terminal Page

Open:

```text
http://localhost:8080/terminal
```

The page loads the xterm.js assets bundled inside the sandbox:

```text
/static/sandbox/xterm@5.3.0/
/static/sandbox/xterm-addon-fit@0.8.0/
```

Local previews do not depend on an external CDN. The page connects to `ws://localhost:8080/v1/shell/ws`, creates a new terminal session, and writes the returned `session_id` into the URL so the UI can identify the active session.

## WebSocket Endpoint

Connect your custom UI to a new session:

```text
ws://localhost:8080/v1/shell/ws
```

After the connection is established, the server returns a `session_id` so your UI can identify the active session. After connection failures, create a new terminal session instead of relying on `ws?session_id=...` for disconnect recovery or history restoration.

## Message Types

Client to server:

```json
{ "type": "input", "data": "ls -la\n" }
{ "type": "resize", "data": { "cols": 120, "rows": 40 } }
{ "type": "pong", "data": { "timestamp": 1710000000000 } }
```

Server to client:

```json
{ "type": "session_id", "data": "SESSION_ID" }
{ "type": "ready", "data": "Terminal ready" }
{ "type": "output", "data": "command output" }
{ "type": "ping", "timestamp": 1710000000000 }
```

`input` is the raw terminal input stream, so include a newline when executing commands. Send `resize` when the terminal container changes size. Only reply with `pong` after receiving an application-level `ping`.

## Minimal Browser Example

This example loads xterm.js from AIO's bundled static assets and connects a local page to a local sandbox.

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <link
      rel="stylesheet"
      href="http://localhost:8080/static/sandbox/xterm@5.3.0/css/xterm.css"
    />
    <style>
      html,
      body,
      #terminal {
        width: 100%;
        height: 100%;
        margin: 0;
      }
    </style>
  </head>
  <body>
    <div id="terminal"></div>

    <script src="http://localhost:8080/static/sandbox/xterm@5.3.0/lib/xterm.js"></script>
    <script src="http://localhost:8080/static/sandbox/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>
    <script>
      const term = new Terminal({ cursorBlink: true, convertEol: true });
      const fitAddon = new FitAddon.FitAddon();
      term.loadAddon(fitAddon);
      term.open(document.getElementById("terminal"));
      fitAddon.fit();

      const ws = new WebSocket("ws://localhost:8080/v1/shell/ws");

      ws.addEventListener("open", () => {
        ws.send(JSON.stringify({
          type: "resize",
          data: { cols: term.cols, rows: term.rows },
        }));
      });

      term.onData((data) => {
        ws.send(JSON.stringify({ type: "input", data }));
      });

      ws.addEventListener("message", (event) => {
        const message = JSON.parse(event.data);

        if (message.type === "output") {
          term.write(message.data);
        }

        if (message.type === "ping") {
          ws.send(JSON.stringify({
            type: "pong",
            data: { timestamp: message.timestamp ?? message.data },
          }));
        }
      });

      window.addEventListener("resize", () => {
        fitAddon.fit();
        ws.send(JSON.stringify({
          type: "resize",
          data: { cols: term.cols, rows: term.rows },
        }));
      });
    </script>
  </body>
</html>
```

For the complete Shell protocol, see [Shell Terminal](/guide/basic/shell).
