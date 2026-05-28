# 屏幕录制

AIO Sandbox 可以录制完整桌面画面并保存为 MP4 文件。录制内容包括浏览器 UI、多标签页、弹窗、终端窗口以及所有可见桌面操作。

如果需要完整视觉审计记录，请使用屏幕录制。如果只需要单个页面内容，可以使用浏览器页面录制。

## 开始录制

```bash
curl -X POST "http://localhost:8080/v1/display/record" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "start",
    "save_path": "/home/gem/recordings/session.mp4"
  }'
```

## 查询状态

```bash
curl -X POST "http://localhost:8080/v1/display/record" \
  -H "Content-Type: application/json" \
  -d '{"action": "status"}'
```

## 停止录制

```bash
curl -X POST "http://localhost:8080/v1/display/record" \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'
```

## 使用建议

- 将录制文件保存到工作目录或其他已知目录，便于通过文件 API 下载。
- 如果需要完整可播放文件，请在删除容器前停止录制。
- 调试和验收场景建议控制录制时长，避免文件过大。

## 相关内容

- [浏览器自动化](/zh/guide/basic/browser)
- [文件操作](/zh/guide/basic/file)
