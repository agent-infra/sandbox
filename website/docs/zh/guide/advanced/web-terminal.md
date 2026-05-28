# WebTerminal 集成

AIO Sandbox 提供内置 Web Terminal 页面，也暴露 Shell WebSocket 端点，方便把终端嵌入到你自己的本地 Web UI 中。

下面示例默认 AIO Sandbox 运行在 `http://localhost:8080`。

## 内置终端页面

直接打开：

```text
http://localhost:8080/terminal
```

该页面会加载沙盒内置的 xterm.js 静态资源：

```text
/static/sandbox/xterm@5.3.0/
/static/sandbox/xterm-addon-fit@0.8.0/
```

因此本地预览不依赖外部 CDN。页面会自动连接 `ws://localhost:8080/v1/shell/ws`，创建新终端会话，并在 URL 中写入返回的 `session_id` 方便 UI 标识当前会话。

## WebSocket 端点

自定义 UI 直接连接新会话：

```text
ws://localhost:8080/v1/shell/ws
```

连接成功后服务端会返回 `session_id`，方便 UI 标识当前会话。连接异常时建议重新创建终端会话，不要依赖 `ws?session_id=...` 做断线恢复或历史恢复。

## 消息类型

客户端发送：

```json
{ "type": "input", "data": "ls -la\n" }
{ "type": "resize", "data": { "cols": 120, "rows": 40 } }
{ "type": "pong", "data": { "timestamp": 1710000000000 } }
```

服务端发送：

```json
{ "type": "session_id", "data": "SESSION_ID" }
{ "type": "ready", "data": "Terminal ready" }
{ "type": "output", "data": "command output" }
{ "type": "ping", "timestamp": 1710000000000 }
```

`input` 是终端原始输入流，执行命令时记得带换行符。`resize` 应在终端容器尺寸变化时发送。只有收到应用层 `ping` 时才需要回复 `pong`。

## 最小浏览器示例

这个示例用 AIO 内置静态资源加载 xterm.js，并从本地页面连接本地沙盒。

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

完整 Shell 协议见 [Shell 终端](/zh/guide/basic/shell)。
