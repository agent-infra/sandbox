# 文档与中文文本处理工具

这是一个可选的 AIO 扩展镜像示例，为 Agent 预装文档和中文文本处理依赖，沿用 AIO 的服务与启动方式。

- `pandoc`、Poppler：文档转换、PDF 文本提取和渲染。
- `sqlite3`、`fd`：本地结构化数据处理和文件查找。
- `python-docx`、`ebooklib`、`pypdf`：处理 DOCX、EPUB、PDF。
- `Markdown`、`PyYAML`、`chardet`：Markdown 渲染、YAML 解析、编码识别。
- `jieba`、`opencc-python-reimplemented`：中文分词、繁简转换。

Python 库安装到 AIO 1.11.0 的系统 `/usr/bin/python3`，其他虚拟环境不会自动继承。未添加旧版 `.doc` 转换工具或 OCR 引擎。

在仓库根目录构建：

```bash
docker build -t aio-document-tools:local \
  --build-arg BASE_IMAGE=enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:1.11.0 \
  examples/document-chinese-tools
```

构建时会执行 `smoke_test.py`，生成临时 DOCX、EPUB、PDF 文件，验证读写、转换和中文处理；检查失败会使构建失败。测试无需服务、凭据或网络，安装依赖时需要网络。

启动方法和镜像体积增量的核对命令见 [英文说明](./README.md)。
