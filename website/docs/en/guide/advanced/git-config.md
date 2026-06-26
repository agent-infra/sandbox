# Git Configuration

Git is commonly used to bring source code into the sandbox or commit generated changes.

## Public Repositories

Clone public repositories directly:

```bash
git clone https://github.com/user/repo.git /home/gem/repo
```

For faster startup, bake stable repositories into a custom image:

```dockerfile
FROM ghcr.io/agent-infra/sandbox:latest
RUN git clone --depth 1 https://github.com/user/repo.git /home/gem/repo
```

## Private Repositories

For private repositories, prefer runtime credentials instead of baking secrets into images:

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 127.0.0.1:8080:8080 \
  -e GIT_ASKPASS=/home/gem/git-askpass.sh \
  ghcr.io/agent-infra/sandbox:latest
```

You can also mount SSH keys or token files for a single task, then remove them when the task is complete.

## Recommended Settings

```bash
git config --global user.name "AIO Sandbox"
git config --global user.email "sandbox@example.com"
git config --global init.defaultBranch main
```

## Security

- Never commit secrets into the repository.
- Avoid adding private keys to custom image layers.
- Prefer short-lived tokens for one-off tasks.
- Review generated diffs before pushing changes.

