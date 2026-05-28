# 工具

AIO Sandbox 提供了一些面向 Agent 常见任务的工具 API。当前公开工具能力包括内容转 Markdown。

## 转换为 Markdown

使用 `/v1/util/convert_to_markdown` 将 URI 内容转换为 Markdown 文本。

```bash
curl -X POST "http://localhost:8080/v1/util/convert_to_markdown" \
  -H "Content-Type: application/json" \
  -d '{
    "uri": "https://example.com"
  }'
```

响应可以交给 Agent，总结后写入文件，或与浏览器自动化结果结合使用。

## 使用场景

- 总结前先把公开网页转换为 Markdown。
- 下载文档到沙盒文件系统后再转换。
- 在索引或检索前统一内容格式。

## 相关内容

- [文件操作](/zh/guide/basic/file)
- [浏览器自动化](/zh/guide/basic/browser)
- [统一代码执行](/zh/guide/basic/code)

