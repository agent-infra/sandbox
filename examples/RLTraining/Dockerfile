FROM ghcr.io/agent-infra/sandbox:latest

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Install the nono CLI, used to confine each rollout to its working directory.
RUN VERSION=$(curl -k -sI https://github.com/always-further/nono/releases/latest | grep -i location | sed -E 's|.*/tag/v?([^[:space:]\r]+).*|\1|') && \
    ARCH=$(dpkg --print-architecture) && \
    wget --no-check-certificate -O /tmp/nono.deb https://github.com/always-further/nono/releases/download/v${VERSION}/nono-cli_${VERSION}_${ARCH}.deb && \
    dpkg -i /tmp/nono.deb && \
    rm -f /tmp/nono.deb
