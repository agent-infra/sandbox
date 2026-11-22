"""Exercise document tools using generated fixtures; no network or services needed."""
import shutil
import subprocess
import tempfile
from pathlib import Path

import chardet
import jieba
import markdown
import yaml
from docx import Document
from ebooklib import epub
from opencc import OpenCC
from pypdf import PdfReader, PdfWriter


def run(*args):
    return subprocess.check_output(args, text=True)


def main():
    for command in ("pandoc", "pdftotext", "pdfinfo", "sqlite3", "fd"):
        if not shutil.which(command):
            raise RuntimeError(f"Missing command: {command}")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        doc = Document()
        doc.add_paragraph("Document round trip")
        doc.save(root / "sample.docx")
        assert Document(root / "sample.docx").paragraphs[0].text == "Document round trip"
        assert "Document round trip" in run("pandoc", str(root / "sample.docx"), "-t", "plain")

        book = epub.EpubBook()
        book.set_identifier("document-tools-smoke-test")
        book.set_title("Sample")
        book.set_language("en")
        chapter = epub.EpubHtml(title="Chapter", file_name="chapter.xhtml", lang="en")
        chapter.content = "<h1>EPUB round trip</h1>"
        book.add_item(chapter)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.toc = (chapter,)
        book.spine = ["nav", chapter]
        epub.write_epub(str(root / "sample.epub"), book)
        restored = epub.read_epub(str(root / "sample.epub"))
        assert b"EPUB round trip" in restored.get_item_with_href("chapter.xhtml").get_content()

        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.write(root / "sample.pdf")
        assert len(PdfReader(root / "sample.pdf").pages) == 1
        run("pdfinfo", str(root / "sample.pdf"))
        assert not run("pdftotext", str(root / "sample.pdf"), "-").strip()
        assert run("sqlite3", ":memory:", "select 6 * 7;").strip() == "42"
        assert "sample.docx" in run("fd", "sample", str(root))

    assert OpenCC("t2s").convert("繁體中文") == "繁体中文"
    assert " ".join(jieba.cut("中文分词测试")).replace(" ", "") == "中文分词测试"
    assert "<h1>Title</h1>" in markdown.markdown("# Title")
    assert yaml.safe_load("title: sample") == {"title": "sample"}
    assert chardet.detect(b"plain text")["encoding"] == "ascii"
    print("Document and Chinese text tools: OK")


if __name__ == "__main__":
    main()
