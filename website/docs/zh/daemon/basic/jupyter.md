# Jupyter

`/v1/jupyter` 在真正的 IPython kernel 里执行 Python。它覆盖原生 Python REPL 做不到的场景，代价是进程开销更大：

- 富输出（`display_data` mime bundle，比如 matplotlib 的 PNG）
- IPython magic 命令
- 在已装的多个 Python 版本之间选择

`aiod` 自己实现这一层：启动 `ipykernel`，直接用 Jupyter kernel 协议与它通信。不涉及 Jupyter server，也不需要额外起任何东西。

![](/architecture/aiod-jupyter-kernel.svg)

## 运行要求

`aiod` 选用的 Python 解释器必须能 `import ipykernel`。如果没有安装，请先执行 `pip install ipykernel`，再启动 daemon。

daemon 只在启动时探测一次。安装完成后，重启 daemon，再检查 `GET /v1/capabilities`：`code_interpreter.jupyter_backend` 应为 `"kernel"`，`python_kernels` 会列出可用的 kernel。

未安装时，`/v1/jupyter/*` 路由不可用，并会说明修复方式；`/v1/code/info` 也不会声明 `jupyter` 这一 kind。

如果设置了 `AIO_JUPYTER_ENDPOINT` 且可以连接，外部 Jupyter server 会优先于内嵌 kernel，daemon 会将 `/v1/jupyter` 原样代理到该服务。

## 执行代码单元

提交这一格的源码，响应中包含 notebook 输出：

```bash
curl -X POST "$BASE_URL/v1/jupyter/execute" \
  -H "Content-Type: application/json" \
  -d '{"code": "from IPython.display import HTML\nHTML(\"<b>hi</b>\")"}'
```

请求体示例：

```json
{
  "code": "from IPython.display import HTML\nHTML(\"<b>hi</b>\")"
}
```

`data` 是：

- `code` —— 实际运行的代码
- `status` —— `ok`、`error` 或 `timeout`
- `execution_count` —— kernel 的 cell 计数器
- `outputs` —— notebook 输出对象（`stream`、`execute_result`、`display_data`、`error`）
- `session_id` —— 运行它的会话；一次性执行时是 `null`
- `kernel_name` —— 运行它的 kernel
- `msg_id` —— 该请求的 Jupyter 消息 id

每个输出对象上所有键都在，用不到的是 `null`，所以客户端可以直接读 `outputs[i].text` 或 `outputs[i].data`，不必先按类型分支。

请求体字段：

| 字段 | 取值 | 含义 |
| --- | --- | --- |
| `code` | required | cell 源码；空 cell 也会执行并返回 `ok` |
| `session_id` | optional | 复用时在同一命名空间里继续 |
| `stateful` | `true` | 为 true 时返回会话 id |
| `kernel_name` | `available_kernels` 之一，默认取第一个 | 用哪个已装的 kernel 运行 |
| `timeout` | 1–900 秒（默认 30） | 超时的 cell 会被中断 |
| `cwd` | optional | 在 kernel 启动时固定；传新值会启动新 kernel |

daemon 不支持的 `kernel_name` 返回 `422`，例如：`unknown kernel 'ir'; available: python3, python3.14`。

`cwd` 不是目录不算请求错误。该 cell 返回 `200`，`success` 为 `false`，并带一条写明路径的 `DirectoryError` 输出。

## 查看 kernel 信息

```bash
curl "$BASE_URL/v1/jupyter/info"
```

`available_kernels` 是探测出来的，不是声明的：里面的每个名字都可以作为 `kernel_name` 传进来。返回里还有 `description` 和 `kernel_detection` 两行，给直接看原始 JSON 的人。

## 输出格式

一个输出对象是四种形态之一：

| `output_type` | 携带 | 由什么产生 |
| --- | --- | --- |
| `stream` | `name`（`stdout` 或 `stderr`）和 `text` | `print`，以及 `%time` 这类 magic |
| `execute_result` | `data` mime bundle 和 `execution_count` | cell 的最后一个表达式 |
| `display_data` | `data` mime bundle，含 `image/png` | `display()`，以及 `%matplotlib inline` 的图 |
| `error` | `ename`、`evalue`、`traceback` | 抛出的异常；`status` 变成 `error` |

matplotlib 要返回 PNG，需要使用 `%matplotlib inline`。只使用 `Agg` 后端时，图会写入文件，该 cell 不返回 `display_data`。

```python
client = Sandbox(base_url=BASE_URL)

# 1. Open a session and load the data in it.
client.jupyter.execute_code(
    session_id="report",
    code="import pandas as pd\ndf = pd.DataFrame({'v': [120, 135, 150]})",
)

# 2. A chart comes back as a PNG in display_data.
run = client.jupyter.execute_code(
    session_id="report",
    code="%matplotlib inline\ndf.plot()",
    timeout=120,
).data
for out in run.outputs:
    print(out.output_type, sorted((out.data or {}).keys()))

# 3. End the session; its kernel goes with it.
client.jupyter.delete_session("report")
```

`image/png` 是 base64，这张图大约 27 KB。cell 写入的文件也是普通文件：通过 [文件 API](/zh/daemon/basic/file) 读取。

## 一次性执行与会话

不传 `session_id` 和 `stateful: true` 时，请求只执行一次。daemon 会从预热池取一个 kernel；没有可用 kernel 时，再为这次请求启动一个。执行结束后，kernel 也会关闭。

因此，一次性执行中定义的变量不会保留到下一次请求。再次使用时会得到 `NameError`。

传 `stateful: true` 后，响应会返回一个会话 id；也可以自行指定 `session_id`。后续请求带上同一个 id，就会在同一个命名空间中继续执行。

一个会话在整个生命周期内独占一个 kernel，`execution_count` 会在多次调用之间连续累加。

| 路由 | 作用 | 说明 |
| --- | --- | --- |
| `POST /v1/jupyter/sessions/create` | 提前开一个会话 | 接受 `kernel_name`、`cwd`、`session_id` |
| `GET /v1/jupyter/sessions` | 列出全部 | 每条带 `kernel_name`、`cwd`、`state` |
| `GET /v1/jupyter/sessions/{id}` | 读取一个 | 未知 id 返回 `404` |
| `DELETE /v1/jupyter/sessions/{id}` | 结束一个 | 未知 id 返回 `200`，`success` 为 `false` |
| `DELETE /v1/jupyter/sessions` | 结束全部 | 返回 `cleaned_sessions` |

会话没有 interrupt 和 restart：超过 `timeout` 的 cell 会被自动中断，结束会话用 `DELETE`。这两个路径返回 `501` 并说明这一点。

会话由 kernel 和 id 共同标识。因此，默认 kernel 上的 `s1` 与另一个 kernel 上的 `s1` 属于两个不同的命名空间。

后者会以组合键 `python3.14:s1` 列出。如果该 kernel 同时支撑 [Code](/zh/daemon/basic/code) 路由，在那里传相同的 id 也会访问该会话的命名空间。

kernel 的工作目录在启动时固定。请求的 `cwd` 与池里所有 kernel 都不同时，会启动一个新 kernel；池里的 kernel 不会被移动。

## 超时与输出上限

一个 cell 超过 `timeout` 后，daemon 会先通过 control 通道发送 `interrupt_request`，再等待 2 秒。

如果 kernel 及时停止，会话仍然保留，cell 的 `status` 为 `"timeout"`。输出中会先出现 `KeyboardInterrupt`，再出现 `execution timed out after 2000ms and was interrupted`。

忽略中断的 kernel 会被终止，会话随之丢弃。

每个 cell 最多返回 2,000,000 个字符。流式文本超过上限时，保留开头部分，并追加一条 `stderr`：`[output truncated at 2000000 characters]`。

同一个 cell 后续产生的输出仍会返回，额外保留 64 KiB。单条结果或图片超过上限时无法截断，会直接丢弃，并只保留这条提示。

最多同时运行 5 个会话（`AIO_KERNEL_MAX_SESSIONS`），每个会话空闲 300 秒后回收（`AIO_KERNEL_SESSION_TIMEOUT_SECS`）。

第 6 个会话请求返回 `429`，消息为 `Maximum number of kernel sessions (5) reached`。已有会话不会被清除。

一个 kernel 占用约 60 MB 内存。这两个上限比原生 REPL 的 20 个会话 / 1800 秒更紧。

`AIO_KERNEL_PREWARM`（默认 `0`）保持这么多个空闲 kernel 预热。启动后的第一个 cell 因此是约 90 ms 而不是 1.4 秒。池在启动时填满，每次用掉后在后台补充。

## 内存占用

在相同资源限制下，对比 `aiod` 和 1.x 发布镜像。两边都限制为 0.5 CPU / 0.5 GiB；`aiod` 运行 nginx 和一个预热 kernel，1.x 镜像开启 Jupyter，关闭浏览器和 VNC。

![](/architecture/aiod-jupyter-footprint.svg)

kernel 本身的占用相近，主要差异来自外围服务：容器空闲时，`aiod` 占用 69.8 MB，1.x 镜像占用 248.4 MB。
| 首次响应 | 0.42 s | 6.9 s |
| 会话执行 p50 | 6.4 ms | 11.1 ms |

## 相关页面

- [Code](/zh/daemon/basic/code) —— 统一的代码执行路由，以及 Python 后端的选择方式
- [Node.js](/zh/daemon/basic/nodejs) —— JavaScript REPL
