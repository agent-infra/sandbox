# 可观测性

aiod 向 stdout 写 JSON 日志，在 `GET /metrics` 提供 Prometheus 指标，配置端点后上报 OpenTelemetry trace。默认不主动推送。

## 日志

stdout 上每个请求一行 JSON，标记为 `HTTP_REQUEST`，挂在 `app.request` 这一 target 上。内容包括：

| 字段 | 含义 |
| --- | --- |
| `method`、`path`、`route` | 这次请求，以及它匹配到的路由模板 |
| `status`、`duration_ms` | HTTP 状态码，以及响应耗时（毫秒） |
| `logid`、`client_ip` | 请求 id，以及调用方地址 |
| `success`、`error_kind`、`error_message` | 处理结果，以及失败原因 |
| `query`、`path_params`、`request`、`response` | 进来的内容和返回的内容 |
| `trace_id`、`span_id` | 开了 trace 上报时才有 |

凭证会在写入日志前脱敏。

名称包含以下标记的 query 参数或 body 字段会被替换：`api_key`、`authorization`、`token`、`password`、`secret`、`cookie` 和 `ticket`。

替换后的值包含长度和一段短 SHA-256，可以区分不同值，但不会暴露原始内容：

```json
{
  "path": "/v1/bash/exec",
  "status": 200,
  "request": {
    "captured": true,
    "size": 42,
    "sha256": "9833e0d76731",
    "params": {
      "command": "echo hi",
      "password": {
        "redacted": true,
        "len": 7,
        "sha256": "f52fbd32b2b3"
      }
    }
  }
}
```

只有满足以下条件的 JSON body 才会被摘要：`application/json`、带明确的 `Content-Length`，且大小不超过 8 KiB。

上传、流式请求、WebSocket 握手和超出上限的 body 不会被摘要。日志条目会使用 `captured: false`，并通过 `reason` 说明原因；body 仍会逐字节交给 handler。

请求 id 按以下顺序获取：`x-tt-logid`、`x-logid`、`x-log-id`、`x-request-id`。

这些请求头都不存在时，系统会生成一个 id。响应通过 `x-tt-logid` 返回该 id，并将同一个 id 传给 computer-use，因此一个 id 可以关联两个进程：

```bash
curl -sD - -o /dev/null "$BASE_URL/v1/ping" -H "x-tt-logid: my-trace-1" | grep logid
# x-tt-logid: my-trace-1
```

| 变量 | 默认值 | 作用 |
| --- | --- | --- |
| `AIO_RUST_LOG_LEVEL` | `info` | 日志级别，也接受 `aio_daemon=debug,info` 这样的 `tracing` 过滤表达式 |

## 指标

```bash
curl "$BASE_URL/metrics" -H "Authorization: Bearer <key>"
```

Prometheus 文本格式，按请求生成。设置了 API key 时，`/metrics` 需要携带 key。一共四组指标：

| 指标 | 类型 | 标签 |
| --- | --- | --- |
| `http_requests_total` | Counter | `method`、`route`、`status` |
| `http_request_duration_seconds` | Histogram | 无；整个进程一条耗时分布 |
| `command_exec_total` | Counter | 无 |
| `command_exec_duration_seconds` | Histogram | 无 |

两个 histogram 用同一套分桶，从 1 毫秒到 30 秒。没有匹配到路由的请求统一归到 `<unmatched>` 标签，因此扫描端点不会让时间序列数量失控。

## OpenTelemetry Trace

默认关闭。通过环境变量启用：

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317 aiod start
```

| 变量 | 默认值 | 作用 |
| --- | --- | --- |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | 未设置 | 配置后开启 trace 上报 |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc` | `grpc` 或 `http/protobuf` |
| `OTEL_EXPORTER_OTLP_HEADERS` | 未设置 | collector 鉴权用的请求头 |
| `OTEL_EXPORTER_OTLP_TIMEOUT` | `10000` | 上报超时，单位毫秒 |
| `OTEL_SERVICE_NAME` | `aiod`（worker 为 `computer-use`） | 打在 span 上的服务名 |
| `OTEL_RESOURCE_ATTRIBUTES` | 未设置 | 附加的资源属性 |
| `OTEL_SDK_DISABLED` | 未设置 | 设为 `true` 则即使配了端点也不上报 |

带 `_TRACES_` 的专用变量优先于通用变量。

使用 `http/protobuf` 时，通用端点会被视为 base URL，并自动追加 `/v1/traces`；`OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` 则按原值使用。

每个请求一个 span（`otel.kind` 为 `server`，带 `http.method` 和 `http.route`）。trace context 透传：调用方的 trace 会经 daemon 转发到 computer-use。

![](/screenshots/aiod-jaeger-trace.png)

只支持明文 `http://` 的 collector：构建里没有编入 TLS 后端。

## 相关页面

- [鉴权](/zh/daemon/basic/authentication) —— `/metrics` 的 key 配置
- [错误处理](/zh/daemon/basic/error-handling) —— `error_kind` 对应的状态码
