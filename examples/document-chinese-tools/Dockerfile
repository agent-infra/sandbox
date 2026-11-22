# Extend AIO without replacing its entrypoint, services, user, or package mirrors.
ARG BASE_IMAGE=ghcr.io/agent-infra/sandbox:1.11.0
FROM ${BASE_IMAGE}

RUN apt-get update \
    && apt-get install -y --no-install-recommends pandoc poppler-utils sqlite3 fd-find \
    && ln -sf /usr/bin/fdfind /usr/local/bin/fd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/document-tools-requirements.txt
RUN /usr/bin/python3 -m pip install --no-cache-dir -r /tmp/document-tools-requirements.txt \
    && rm /tmp/document-tools-requirements.txt

COPY smoke_test.py /tmp/document-tools-smoke-test.py
RUN /usr/bin/python3 /tmp/document-tools-smoke-test.py \
    && rm /tmp/document-tools-smoke-test.py
