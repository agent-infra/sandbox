# 安全

默认情况下，本地 AIO Sandbox 面向可信本地开发使用。当需要暴露给网络或其他服务时，应增加鉴权并限制访问范围。

## JWT 鉴权

设置 `JWT_PUBLIC_KEY` 可以启用 Bearer token 校验。业务侧使用私钥签发 token，沙盒使用公钥验证 token。

生成密钥对：

```bash
openssl genrsa -out private_key.pem 2048
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

启动沙盒并注入公钥：

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 8080:8080 \
  -e JWT_PUBLIC_KEY="$(base64 -w 0 public_key.pem)" \
  ghcr.io/agent-infra/sandbox:latest
```

调用 API 时携带 Bearer token：

```bash
curl "http://localhost:8080/v1/sandbox" \
  -H "Authorization: Bearer $SANDBOX_TOKEN"
```

## 短时票据

对于浏览器访问或临时交接流程，如果部署形态支持，优先使用短时票据。票据应尽快过期，并限制在最小必要访问范围内。

## 网络边界

- 不需要远程访问时，只绑定到 localhost。
- 共享环境中建议在沙盒前放置带 TLS 的反向代理。
- 通过 IP、网络或服务身份限制入站访问。
- 不要把未鉴权的沙盒 API 暴露到公网。

## 密钥处理

- 通过运行时环境变量或密钥管理系统传入密钥。
- 不要把密钥写入自定义镜像。
- 不要把长期密钥写入 Skills、Hooks、Notebook 或生成文件。
- 任务级访问优先使用短时凭据。

