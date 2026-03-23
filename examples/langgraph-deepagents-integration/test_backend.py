"""Systematic test for all AIOSandboxBackend methods and parameters."""

import base64
import json
import os
import sys

from agent_sandbox import Sandbox
from sandbox_backend import AIOSandboxBackend

os.environ["NO_PROXY"] = "localhost,127.0.0.1"

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []


def test(name, fn):
    try:
        result = fn()
        print(f"  {PASS} {name}")
        if result is not None:
            # Print truncated result for inspection
            s = str(result)
            print(f"       → {s[:200]}{'...' if len(s) > 200 else ''}")
        results.append((name, True, None))
        return result
    except Exception as e:
        print(f"  {FAIL} {name}: {e}")
        results.append((name, False, str(e)))
        return None


def main():
    sandbox_url = os.getenv("SANDBOX_URL", "http://localhost:8080")
    client = Sandbox(base_url=sandbox_url, timeout=300)

    with AIOSandboxBackend(client, working_dir="/home/tiger") as backend:
        # ============================================================
        # 1. execute(command, *, timeout=None)
        # ============================================================
        print("\n== 1. execute ==")

        # 1a. basic command
        test("execute: basic command",
             lambda: backend.execute("echo hello"))

        # 1b. command with exit code != 0 (use subshell, not bare exit)
        test("execute: non-zero exit code",
             lambda: backend.execute("bash -c 'exit 42'"))

        # 1c. explicit timeout parameter
        test("execute: with timeout",
             lambda: backend.execute("sleep 1 && echo done", timeout=30))

        # 1d. timeout=None (default)
        test("execute: timeout=None (default)",
             lambda: backend.execute("echo default_timeout", timeout=None))

        # 1e. multi-line output
        test("execute: multi-line output",
             lambda: backend.execute("echo line1; echo line2; echo line3"))

        # 1f. stderr output
        test("execute: stderr",
             lambda: backend.execute("echo err >&2"))

        # ============================================================
        # 2. write(file_path, content)
        # ============================================================
        print("\n== 2. write ==")

        # cleanup
        backend.execute("rm -rf /home/tiger/test_dir")
        backend.execute("mkdir -p /home/tiger/test_dir")

        # 2a. create new file
        test("write: create new file",
             lambda: backend.write("/home/tiger/test_dir/new.txt", "hello world"))

        # 2b. error if file already exists
        test("write: error on existing file",
             lambda: backend.write("/home/tiger/test_dir/new.txt", "overwrite"))

        # 2c. create file with unicode content
        test("write: unicode content",
             lambda: backend.write("/home/tiger/test_dir/unicode.txt", "你好世界 🌍"))

        # 2d. create file with empty content
        test("write: empty content",
             lambda: backend.write("/home/tiger/test_dir/empty.txt", ""))

        # 2e. create file in nested (non-existent) directory
        test("write: nested directory",
             lambda: backend.write("/home/tiger/test_dir/a/b/c/deep.txt", "deep"))

        # ============================================================
        # 3. read(file_path, offset=0, limit=2000)
        # ============================================================
        print("\n== 3. read ==")

        # prep a multi-line file
        backend.execute("seq 1 100 > /home/tiger/test_dir/lines.txt")

        # 3a. basic read (defaults)
        test("read: basic (defaults)",
             lambda: backend.read("/home/tiger/test_dir/new.txt"))

        # 3b. read with offset
        test("read: offset=5",
             lambda: backend.read("/home/tiger/test_dir/lines.txt", offset=5))

        # 3c. read with limit
        test("read: limit=3",
             lambda: backend.read("/home/tiger/test_dir/lines.txt", offset=0, limit=3))

        # 3d. read with offset + limit
        test("read: offset=10, limit=5",
             lambda: backend.read("/home/tiger/test_dir/lines.txt", offset=10, limit=5))

        # 3e. read non-existent file
        test("read: non-existent file",
             lambda: backend.read("/home/tiger/test_dir/nonexistent.txt"))

        # 3f. read empty file
        test("read: empty file",
             lambda: backend.read("/home/tiger/test_dir/empty.txt"))

        # 3g. read unicode file
        test("read: unicode file",
             lambda: backend.read("/home/tiger/test_dir/unicode.txt"))

        # ============================================================
        # 4. edit(file_path, old_string, new_string, replace_all=False)
        # ============================================================
        print("\n== 4. edit ==")

        # prep
        backend.write("/home/tiger/test_dir/edit_test.txt",
                       "foo bar foo baz foo")

        # 4a. basic single replace
        test("edit: single replace",
             lambda: backend.edit("/home/tiger/test_dir/edit_test.txt",
                                  "bar", "BAR"))

        # 4b. replace_all=True
        test("edit: replace_all=True",
             lambda: backend.edit("/home/tiger/test_dir/edit_test.txt",
                                  "foo", "FOO", replace_all=True))

        # 4c. replace_all=False on multi-occurrence (should error)
        backend.write("/home/tiger/test_dir/edit_multi.txt", "aaa bbb aaa")
        test("edit: replace_all=False on multi-occurrence",
             lambda: backend.edit("/home/tiger/test_dir/edit_multi.txt",
                                  "aaa", "AAA", replace_all=False))

        # 4d. string not found in file
        test("edit: string not found",
             lambda: backend.edit("/home/tiger/test_dir/edit_test.txt",
                                  "NONEXISTENT_STRING", "replacement"))

        # 4e. file not found
        test("edit: file not found",
             lambda: backend.edit("/home/tiger/test_dir/no_such_file.txt",
                                  "a", "b"))

        # 4f. edit with unicode strings
        backend.write("/home/tiger/test_dir/edit_unicode.txt", "旧内容在这里")
        test("edit: unicode strings",
             lambda: backend.edit("/home/tiger/test_dir/edit_unicode.txt",
                                  "旧内容", "新内容"))

        # verify edit results
        test("edit: verify single replace result",
             lambda: backend.read("/home/tiger/test_dir/edit_test.txt"))
        test("edit: verify unicode edit result",
             lambda: backend.read("/home/tiger/test_dir/edit_unicode.txt"))

        # ============================================================
        # 5. ls_info(path)
        # ============================================================
        print("\n== 5. ls_info ==")

        # 5a. list directory
        test("ls_info: directory listing",
             lambda: backend.ls_info("/home/tiger/test_dir"))

        # 5b. list root
        test("ls_info: root directory",
             lambda: backend.ls_info("/"))

        # 5c. list non-existent path
        test("ls_info: non-existent path",
             lambda: backend.ls_info("/home/tiger/nonexistent_dir"))

        # 5d. verify FileInfo fields (path, is_dir, size, modified_at)
        def check_fileinfo_fields():
            items = backend.ls_info("/home/tiger/test_dir")
            assert len(items) > 0, "Expected non-empty listing"
            item = items[0]
            assert "path" in item, "Missing 'path' field"
            assert "is_dir" in item, "Missing 'is_dir' field"
            return f"fields present: {list(item.keys())}"
        test("ls_info: verify FileInfo fields",
             check_fileinfo_fields)

        # ============================================================
        # 6. glob_info(pattern, path="/")
        # ============================================================
        print("\n== 6. glob_info ==")

        # 6a. basic glob
        test("glob_info: *.txt pattern",
             lambda: backend.glob_info("*.txt", path="/home/tiger/test_dir"))

        # 6b. recursive glob
        test("glob_info: **/*.txt recursive",
             lambda: backend.glob_info("**/*.txt", path="/home/tiger/test_dir"))

        # 6c. default path (/)
        test("glob_info: default path=/",
             lambda: backend.glob_info("*.txt"))

        # 6d. no matches
        test("glob_info: no matches",
             lambda: backend.glob_info("*.xyz", path="/home/tiger/test_dir"))

        # 6e. specific filename
        test("glob_info: specific file",
             lambda: backend.glob_info("new.txt", path="/home/tiger/test_dir"))

        # ============================================================
        # 7. grep_raw(pattern, path=None, glob=None)
        # ============================================================
        print("\n== 7. grep_raw ==")

        # prep
        backend.execute("echo 'hello world' > /home/tiger/test_dir/grep1.txt")
        backend.execute("echo 'hello python' > /home/tiger/test_dir/grep2.txt")
        backend.execute("echo 'goodbye world' > /home/tiger/test_dir/grep3.log")

        # 7a. basic pattern only
        test("grep_raw: pattern only",
             lambda: backend.grep_raw("hello"))

        # 7b. pattern + path
        test("grep_raw: pattern + path",
             lambda: backend.grep_raw("hello", path="/home/tiger/test_dir"))

        # 7c. pattern + glob filter
        test("grep_raw: pattern + glob=*.txt",
             lambda: backend.grep_raw("hello", glob="*.txt"))

        # 7d. pattern + path + glob
        test("grep_raw: pattern + path + glob",
             lambda: backend.grep_raw("hello", path="/home/tiger/test_dir",
                                      glob="*.txt"))

        # 7e. no matches
        test("grep_raw: no matches",
             lambda: backend.grep_raw("ZZZZNOTFOUND",
                                      path="/home/tiger/test_dir"))

        # 7f. regex pattern
        test("grep_raw: regex pattern",
             lambda: backend.grep_raw("hel.*ld",
                                      path="/home/tiger/test_dir"))

        # ============================================================
        # 8. upload_files(files: list[tuple[str, bytes]])
        # ============================================================
        print("\n== 8. upload_files ==")

        # 8a. single text file
        test("upload_files: single text file",
             lambda: backend.upload_files([
                 ("/home/tiger/test_dir/uploaded.txt", b"uploaded content")
             ]))

        # 8b. multiple files
        test("upload_files: multiple files",
             lambda: backend.upload_files([
                 ("/home/tiger/test_dir/up1.txt", b"file one"),
                 ("/home/tiger/test_dir/up2.txt", b"file two"),
             ]))

        # 8c. binary content (PNG header bytes)
        png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR' + b'\x00' * 20
        test("upload_files: binary content",
             lambda: backend.upload_files([
                 ("/home/tiger/test_dir/test.bin", png_bytes)
             ]))

        # 8d. verify uploaded text content
        def verify_upload():
            r = backend.read("/home/tiger/test_dir/uploaded.txt")
            assert "uploaded content" in r, f"Expected 'uploaded content' in: {r}"
            return r
        test("upload_files: verify content",
             verify_upload)

        # 8e. empty content
        test("upload_files: empty bytes",
             lambda: backend.upload_files([
                 ("/home/tiger/test_dir/empty.bin", b"")
             ]))

        # ============================================================
        # 9. download_files(paths: list[str])
        # ============================================================
        print("\n== 9. download_files ==")

        # 9a. single file
        test("download_files: single file",
             lambda: backend.download_files(["/home/tiger/test_dir/uploaded.txt"]))

        # 9b. multiple files
        test("download_files: multiple files",
             lambda: backend.download_files([
                 "/home/tiger/test_dir/up1.txt",
                 "/home/tiger/test_dir/up2.txt",
             ]))

        # 9c. non-existent file (should return error)
        test("download_files: non-existent file",
             lambda: backend.download_files(["/home/tiger/test_dir/no_such.txt"]))

        # 9d. binary file roundtrip
        def binary_roundtrip():
            resps = backend.download_files(["/home/tiger/test_dir/test.bin"])
            downloaded = resps[0].content
            assert downloaded == png_bytes, (
                f"Binary roundtrip failed: got {len(downloaded)} bytes, "
                f"expected {len(png_bytes)}"
            )
            return f"roundtrip OK, {len(downloaded)} bytes match"
        test("download_files: binary roundtrip",
             binary_roundtrip)

        # 9e. mixed existing and non-existent
        test("download_files: mixed existing/non-existent",
             lambda: backend.download_files([
                 "/home/tiger/test_dir/up1.txt",
                 "/home/tiger/test_dir/no_such.txt",
             ]))

        # 9f. verify text content
        def verify_download_content():
            resps = backend.download_files(["/home/tiger/test_dir/up1.txt"])
            content = resps[0].content.decode("utf-8")
            assert content == "file one", f"Expected 'file one', got '{content}'"
            return content
        test("download_files: verify text content",
             verify_download_content)

    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "=" * 60)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    print(f"Total: {len(results)} | {PASS}: {passed} | {FAIL}: {failed}")

    if failed:
        print(f"\nFailed tests:")
        for name, ok, err in results:
            if not ok:
                print(f"  - {name}: {err}")
        sys.exit(1)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
