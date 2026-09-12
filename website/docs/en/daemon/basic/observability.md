# Observability

aiod writes JSON logs to stdout, serves Prometheus metrics on `GET /metrics`, and exports OpenTelemetry traces when an endpoint is configured. Nothing is pushed by default.

## Logs

One JSON line per request on stdout, tagged `HTTP_REQUEST` and carried on the `app.request` target. The payload:

| Field | Meaning |
| --- | --- |
| `method`, `path`, `route` | The request, and the path template it matched |
| `status`, `duration_ms` | The HTTP status, and time to answer in milliseconds |
| `logid`, `client_ip` | The request id, and the caller's address |
| `success`, `error_kind`, `error_message` | The outcome, and why it failed |
| `query`, `path_params`, `request`, `response` | What came in and what went back |
| `trace_id`, `span_id` | Added while trace export is on |

Credentials are redacted before the line is written. A query parameter or body field whose name contains a known marker — `api_key`, `authorization`, `token`, `password`, `secret`, `cookie`, `ticket`, and the rest of that family — is replaced by its length and a short SHA-256, enough to tell two values apart without carrying either:

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

Only a bounded JSON body is summarized like that: `application/json`, an explicit `Content-Length`, and at most 8 KiB. An upload, a stream, a WebSocket handshake, and anything larger pass through untouched, and the entry says so with `captured: false` and a `reason`. The body still reaches the handler byte for byte.

aiod takes the request id from `x-tt-logid`, `x-logid`, `x-log-id`, or `x-request-id`, and generates one when the request carries none. It answers with the id in `x-tt-logid` and forwards it to computer-use, so one id spans both processes:

```bash
curl -sD - -o /dev/null "$BASE_URL/v1/ping" -H "x-tt-logid: my-trace-1" | grep logid
# x-tt-logid: my-trace-1
```

| Variable | Default | Effect |
| --- | --- | --- |
| `AIO_RUST_LOG_LEVEL` | `info` | Log level, or any `tracing` filter directive such as `aio_daemon=debug,info` |

## Metrics

```bash
curl "$BASE_URL/metrics" -H "Authorization: Bearer <key>"
```

Prometheus text format, rendered on request. `/metrics` requires the API key when one is set. Four series:

| Series | Type | Labels |
| --- | --- | --- |
| `http_requests_total` | Counter | `method`, `route`, `status` |
| `http_request_duration_seconds` | Histogram | None; one latency distribution for the process |
| `command_exec_total` | Counter | None |
| `command_exec_duration_seconds` | Histogram | None |

Both histograms share the same buckets, 1 ms to 30 s. A request that matched no route folds into a single `<unmatched>` label, so scanning for endpoints cannot blow up the series count.

## OpenTelemetry traces

Off by default. Enable with one variable:

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317 aiod start
```

| Variable | Default | Effect |
| --- | --- | --- |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | unset | Set to enable trace export |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc` | `grpc` or `http/protobuf` |
| `OTEL_EXPORTER_OTLP_HEADERS` | unset | Headers the collector authenticates with |
| `OTEL_EXPORTER_OTLP_TIMEOUT` | `10000` | Export timeout, in milliseconds |
| `OTEL_SERVICE_NAME` | `aiod` (`computer-use` on the worker) | Service name on spans |
| `OTEL_RESOURCE_ATTRIBUTES` | unset | Extra resource attributes |
| `OTEL_SDK_DISABLED` | unset | `true` keeps export off with an endpoint set |

The signal-specific `_TRACES_` spelling of a variable wins over the generic one. Under `http/protobuf` the generic endpoint is a base URL that gets `/v1/traces` appended, while `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` is used as it stands.

One span per request (`otel.kind` `server`, with `http.method` and `http.route`). Trace context propagates: a caller's trace continues through the daemon into computer-use.

![](/screenshots/aiod-jaeger-trace.png)

Only plaintext `http://` collectors are supported: no TLS backend is compiled in.

## Related

- [Authentication](/daemon/basic/authentication) — the key `/metrics` asks for
- [Error Handling](/daemon/basic/error-handling) — the statuses `error_kind` reports
