# Document and Chinese text tools

[中文说明](./README.zh-CN.md)

An opt-in AIO image extension for agents that process DOCX, EPUB, text-based PDF,
Markdown, and Chinese text without installing packages during each session.
It inherits AIO's services and startup behavior.

| Added tools | Use |
| --- | --- |
| pandoc, Poppler (`pdftotext`, `pdfinfo`, rendering tools) | Document conversion and PDF text extraction/rendering |
| sqlite3, fd | Local structured data and file discovery |
| python-docx, ebooklib, pypdf | Read and write DOCX, EPUB, and PDF in Python |
| Markdown, PyYAML, chardet | Markdown rendering, YAML parsing, encoding detection |
| jieba, opencc-python-reimplemented | Chinese tokenization and traditional/simplified conversion |

The Python dependencies are installed into `/usr/bin/python3`, the system Python
in AIO 1.11.0. Other virtual environments do not automatically inherit them.
This example does not add legacy `.doc` conversion or an OCR engine.

## Build and verify

From the repository root:

```bash
docker build -t aio-document-tools:local examples/document-chinese-tools
```

The build runs `smoke_test.py`: generated DOCX/EPUB/PDF fixtures exercise Python
round trips, pandoc conversion, Poppler, SQLite, file discovery, and Chinese text
processing. Any failed check fails the build. The test does not require AIO
services, credentials, or network access; dependency installation does need network.

To use the mainland China base image mirror:

```bash
docker build -t aio-document-tools:local \
  --build-arg BASE_IMAGE=enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:1.11.0 \
  examples/document-chinese-tools
```

Start the image as you would AIO, for example:

```bash
docker run --rm --security-opt seccomp=unconfined \
  -e SANDBOX_API_KEY=your-secret-key \
  -p 127.0.0.1:8080:8080 aio-document-tools:local
```

## Image size

These tools add packages and transitive dependencies, particularly pandoc and
Poppler. Compare the built image with its base on the same architecture:

```bash
docker image inspect ghcr.io/agent-infra/sandbox:1.11.0 aio-document-tools:local \
  --format '{{.RepoTags}} {{.Size}}'
```

Subtract the base size from the extension size for the local uncompressed image
size increase. Registry transfer sizes depend on compression and shared layers.
