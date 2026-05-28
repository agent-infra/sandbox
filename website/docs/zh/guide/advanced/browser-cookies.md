# 浏览器 Cookie 与状态

浏览器状态通常是浏览器自动化中最重要的部分。AIO Sandbox 提供 Cookie 管理以及完整浏览器状态保存/加载 API。

## 设置 Cookie

```bash
curl -X POST "http://localhost:8080/v1/browser/cookies" \
  -H "Content-Type: application/json" \
  -d '{
    "cookies": [
      {
        "name": "session",
        "value": "example",
        "domain": ".example.com",
        "path": "/",
        "secure": true,
        "httpOnly": true
      }
    ]
  }'
```

## 读取或清理 Cookie

自动化准备和清理阶段可以通过浏览器 Cookie API 查看或清理 Cookie。建议使用 API，不要直接操作浏览器 profile 文件。

## 保存浏览器状态

```bash
curl -X POST "http://localhost:8080/v1/browser/state/save" \
  -H "Content-Type: application/json" \
  -d '{"path": "/home/gem/browser-state.json"}'
```

## 加载浏览器状态

```bash
curl -X POST "http://localhost:8080/v1/browser/state/load" \
  -H "Content-Type: application/json" \
  -d '{"path": "/home/gem/browser-state.json"}'
```

## 最佳实践

- 验证 Cookie 行为前，先导航到目标域名。
- 需要恢复完整登录/浏览器状态时，优先使用 state save/load。
- 不要把真实凭据写入提交到仓库的文件。
- 需要与文件 API 共享时，把状态文件放在工作目录内。

