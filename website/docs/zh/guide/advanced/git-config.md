# Git 配置

Git 常用于把源码带入沙盒，或提交 Agent 生成的改动。

## 公开仓库

公开仓库可以直接克隆：

```bash
git clone https://github.com/user/repo.git /home/gem/repo
```

如果仓库版本稳定，也可以预置到自定义镜像中以加快启动：

```dockerfile
FROM ghcr.io/agent-infra/sandbox:latest
RUN git clone --depth 1 https://github.com/user/repo.git /home/gem/repo
```

## 私有仓库

私有仓库建议使用运行时凭据，不要把密钥写入镜像层：

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e GIT_ASKPASS=/home/gem/git-askpass.sh \
  ghcr.io/agent-infra/sandbox:latest
```

也可以为单次任务挂载 SSH key 或 token 文件，任务完成后及时删除。

## 推荐配置

```bash
git config --global user.name "AIO Sandbox"
git config --global user.email "sandbox@example.com"
git config --global init.defaultBranch main
```

## 安全建议

- 不要把密钥提交到仓库。
- 不要把私钥写入自定义镜像层。
- 一次性任务优先使用短时 token。
- 推送改动前先审查生成的 diff。

