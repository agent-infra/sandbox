# 预览代理

AIO Sandbox 包含内置代理端点，允许您直接从开发环境预览和测试 Web 应用程序和服务。

![](/images/port-preview.png)

## 子域代理（推荐）

任何满足 `${port}-${domain}` 格式的域名都将被转发到沙盒内的相应端口。

![](/images/subdomain-proxy.png)

## 基于请求头的端口路由

当公网网关或自建反向代理不适合使用 `${port}-${domain}` 这种 Host 格式时，可以通过注入 `x-aio-proxy-port` 请求头来路由预览流量：

```bash
curl -H 'x-aio-proxy-port: 19877' \
  https://<sandbox-public-host>/some/path
```

沙盒会将请求转发到 `http://127.0.0.1:19877/some/path`。原始路径会保持不变，控制用的请求头会在转发给目标服务前移除。

只有纯数字 header 值会触发该路由。由于该 header 可以选择沙盒内的本地端口，应由可信网关或反向代理覆盖注入，不建议直接信任终端用户传入的同名 header。

## 子路径代理类型

### 前端应用程序代理

使用绝对代理访问前端应用程序：

```
http://localhost:8080/absproxy/{port}/
```

**用例：**
- React、Vue、Angular 应用程序
- 静态站点生成器
- 带有资源打包的开发服务器
- 任何带有开发服务器的前端框架

**示例：**
```bash
# 在端口 3000 上启动 React 应用
cd /workspace/my-react-app
npm start

# 通过代理访问
# 浏览器：http://localhost:8080/absproxy/3000/
```

### 后端服务代理

使用相对代理访问后端服务：

```
http://localhost:8080/proxy/{port}/
```

**用例：**
- API 服务器
- 后端微服务
- 数据库管理界面
- 开发工具和实用程序

**示例：**
```bash
# 在端口 4000 上启动 Express API
cd /workspace/my-api
npm start

# 通过代理访问
# API 端点：http://localhost:8080/proxy/4000/api/users
```

## 下一步

- **终端集成**：通过 Shell 控制服务 → [Shell API](/zh/api/)
- **文件操作**：管理应用程序文件 → [文件 API](/zh/api/)
- **浏览器自动化**：测试应用程序 → [浏览器指南](/zh/guide/basic/browser)
- **高级代理与网络**：配置出站代理和运行时映射 → [代理与网络](/zh/guide/advanced/proxy-network)
