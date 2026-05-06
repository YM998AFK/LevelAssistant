"""AI 可调用的工具实现（分级沙箱）

读操作：允许在 工作目录 / 技能目录 / 用户上传文件 范围内
写操作：只能在工作目录里
"""
from __future__ import annotations

import os
import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import Any, Iterable


class ToolBox:
    def __init__(
        self,
        workspace: Path,
        readable_roots: Iterable[Path] | None = None,
        readable_files: Iterable[str] | None = None,
        extra_writable_roots: Iterable[Path] | None = None,
        mode: str = "",
    ):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.readable_roots = [Path(r).resolve() for r in (readable_roots or []) if r]
        self.readable_files = {
            str(Path(f).resolve()) for f in (readable_files or []) if f
        }
        # 额外可写目录（如 skills/output），写入时自动创建
        self.extra_writable_roots = [Path(r).resolve() for r in (extra_writable_roots or []) if r]
        for p in self.extra_writable_roots:
            p.mkdir(parents=True, exist_ok=True)
        self.mode = mode

    def _is_within(self, child: Path, parent: Path) -> bool:
        try:
            child.resolve().relative_to(parent.resolve())
            return True
        except ValueError:
            return child.resolve() == parent.resolve()

    def _resolve_read(self, path_str: str) -> Path:
        """解析任何读操作的路径：支持相对（基于工作目录）和绝对（需在白名单内）"""
        p = Path(path_str)
        candidate = (p if p.is_absolute() else self.workspace / p).resolve()

        if self._is_within(candidate, self.workspace):
            return candidate
        for root in self.readable_roots:
            if self._is_within(candidate, root):
                return candidate
        if str(candidate) in self.readable_files:
            return candidate
        raise PermissionError(
            f"路径不在允许范围: {path_str}\n"
            f"允许读取：\n  工作目录: {self.workspace}\n"
            + "".join(f"  技能目录: {r}\n" for r in self.readable_roots)
            + ("  用户上传文件：\n" + "".join(f"    - {f}\n" for f in sorted(self.readable_files)) if self.readable_files else "")
        )

    def _resolve_write(self, rel: str) -> Path:
        p = Path(rel)
        if p.is_absolute():
            candidate = p.resolve()
        else:
            candidate = (self.workspace / p).resolve()
        if self._is_within(candidate, self.workspace):
            return candidate
        for root in self.extra_writable_roots:
            if self._is_within(candidate, root):
                return candidate
        raise PermissionError(
            f"写入路径必须在工作目录或输出目录下: {rel}\n"
            f"  工作目录: {self.workspace}\n"
            + "".join(f"  输出目录: {r}\n" for r in self.extra_writable_roots)
        )

    def extract_archive(self, archive_path: str, dest: str = "extracted") -> dict:
        src = self._resolve_read(archive_path)
        if not src.exists():
            return {"error": f"文件不存在: {archive_path}"}
        dst = self._resolve_write(dest)
        dst.mkdir(parents=True, exist_ok=True)
        suffix = "".join(Path(str(src)).suffixes).lower()
        names = []
        try:
            if suffix.endswith(".zip"):
                with zipfile.ZipFile(src) as zf:
                    zf.extractall(dst)
                    names = zf.namelist()
            elif suffix.endswith((".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz")):
                with tarfile.open(src) as tf:
                    tf.extractall(dst)
                    names = tf.getnames()
            elif suffix.endswith(".7z"):
                import py7zr
                with py7zr.SevenZipFile(src) as sz:
                    sz.extractall(dst)
                    names = sz.getnames()
            else:
                return {"error": f"不支持的格式: {suffix}"}
        except Exception as e:
            return {"error": f"解压失败: {type(e).__name__}: {e}"}
        return {"ok": True, "dest": str(dst), "count": len(names), "files": names[:50]}

    def list_dir(self, rel: str = ".") -> dict:
        try:
            p = self._resolve_read(rel)
        except PermissionError as e:
            return {"error": str(e)}
        if not p.exists():
            return {"error": f"不存在: {p}"}
        if not p.is_dir():
            return {"error": f"不是目录: {p}"}
        items = []
        for entry in sorted(p.iterdir()):
            items.append({
                "name": entry.name,
                "type": "dir" if entry.is_dir() else "file",
                "size": entry.stat().st_size if entry.is_file() else None,
            })
        return {"ok": True, "path": str(p), "items": items}

    def read_file(self, rel: str, max_chars: int = 8000) -> dict:
        try:
            p = self._resolve_read(rel)
        except PermissionError as e:
            return {"error": str(e)}
        if not p.exists():
            return {"error": f"不存在: {p}"}
        if p.is_dir():
            return {"error": "是目录，不是文件"}
        try:
            text = p.read_text(encoding="utf-8")
            return {"ok": True, "content": text[:max_chars], "truncated": len(text) > max_chars}
        except UnicodeDecodeError:
            return {"ok": True, "content": f"<binary file, {p.stat().st_size} bytes>", "binary": True}

    def write_file(self, rel: str, content: str) -> dict:
        try:
            p = self._resolve_write(rel)
        except PermissionError as e:
            return {"error": str(e)}
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"ok": True, "path": str(p), "bytes": len(content)}

    def replace_in_file(self, rel: str, old: str, new: str) -> dict:
        try:
            p = self._resolve_write(rel)
        except PermissionError as e:
            return {"error": str(e)}
        if not p.exists():
            return {"error": "不存在"}
        text = p.read_text(encoding="utf-8")
        if old not in text:
            return {"error": "未找到要替换的内容"}
        count = text.count(old)
        p.write_text(text.replace(old, new), encoding="utf-8")
        return {"ok": True, "replaced": count}

    def copy_file(self, src_external: str, dest_rel: str) -> dict:
        """把任何可读路径下的文件复制到工作目录（用于放置替换素材等）"""
        try:
            src = self._resolve_read(src_external)
            dst = self._resolve_write(dest_rel)
        except PermissionError as e:
            return {"error": str(e)}
        if not src.exists():
            return {"error": f"源不存在: {src}"}
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return {"ok": True, "dest": str(dst), "size": dst.stat().st_size}

    def grep_file(
        self,
        pattern: str,
        file_rel: str,
        max_hits: int = 200,
        ignore_case: bool = False,
    ) -> dict:
        """在单个文件中用正则表达式逐行搜索，等价于 `rg <pattern> <file>`。
        专为搜索大型 JSONL / Markdown 资源索引文件设计，无需安装 ripgrep。
        返回所有匹配行的行号和内容，可用于资源搜索、字段提取等场景。
        """
        import re as _re

        try:
            file_path = self._resolve_read(file_rel)
        except PermissionError as e:
            return {"error": str(e)}
        if not file_path.exists():
            return {"error": f"文件不存在: {file_rel}"}
        if not file_path.is_file():
            return {"error": f"不是文件（是目录？）: {file_rel}"}

        flags = _re.IGNORECASE if ignore_case else 0
        try:
            compiled = _re.compile(pattern, flags)
        except _re.error as e:
            return {"error": f"正则表达式无效: {e}"}

        hits: list = []
        truncated = False
        try:
            with open(file_path, encoding="utf-8", errors="replace") as f:
                for i, line in enumerate(f, 1):
                    if compiled.search(line):
                        hits.append({"line": i, "content": line.rstrip()[:600]})
                        if len(hits) >= max_hits:
                            truncated = True
                            break
        except Exception as e:
            return {"error": f"读取失败: {type(e).__name__}: {e}"}

        return {
            "ok": True,
            "file": str(file_path),
            "count": len(hits),
            "truncated": truncated,
            "hits": hits,
        }

    def search_in_files(self, pattern: str, dir_rel: str = ".", max_hits: int = 50) -> dict:
        try:
            root = self._resolve_read(dir_rel)
        except PermissionError as e:
            return {"error": str(e)}
        hits = []
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            if pattern in text:
                for i, line in enumerate(text.splitlines()):
                    if pattern in line:
                        hits.append({
                            "file": str(p),
                            "line": i + 1,
                            "content": line.strip()[:200],
                        })
                        if len(hits) >= max_hits:
                            break
            if len(hits) >= max_hits:
                break
        return {"ok": True, "count": len(hits), "hits": hits}

    def create_archive(self, src_dir: str, output_name: str = "output.zip") -> dict:
        # 硬约束⑥：resource_search 模式只输出文字清单，禁止打包
        if self.mode == "resource_search":
            return {
                "error": (
                    "⛔ [系统强制] resource_search 模式禁止调用 create_archive。"
                    "本模式只输出文字资源清单，不生成任何 zip 文件。"
                    "请直接将资源清单以文字形式输出给用户。"
                )
            }
        try:
            src = self._resolve_write(src_dir) if not Path(src_dir).is_absolute() else self._resolve_read(src_dir)
        except PermissionError as e:
            return {"error": str(e)}
        if not src.exists():
            return {"error": f"源不存在: {src}"}
        # output_name 如果是相对路径，以 output_dir() 的父目录（项目根）为基准
        # 这样 AI 写 "output/modify/xxx.zip" 会落到 项目根/output/modify/xxx.zip
        from .config import output_dir as _output_dir
        out_path = Path(output_name)
        if out_path.is_absolute():
            out = out_path
        else:
            out = _output_dir().parent / output_name
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in src.rglob("*"):
                if p.is_file():
                    zf.write(p, p.relative_to(src))
        return {"ok": True, "archive": str(out), "size": out.stat().st_size}

    def delete_path(self, rel: str) -> dict:
        try:
            p = self._resolve_write(rel)
        except PermissionError as e:
            return {"error": str(e)}
        if not p.exists():
            return {"error": "不存在"}
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return {"ok": True}

    # ── Python 执行工具 ──────────────────────────────────────

    def check_python(self) -> dict:
        """检测系统中是否有可用的 Python 解释器"""
        import subprocess, sys as _sys
        _flags = subprocess.CREATE_NO_WINDOW if _sys.platform == "win32" else 0
        candidates = ["python", "python3", "py"]
        for cmd in candidates:
            try:
                r = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True, text=True, timeout=10,
                    creationflags=_flags,
                )
                if r.returncode == 0:
                    version = (r.stdout or r.stderr).strip()
                    return {"ok": True, "command": cmd, "version": version}
            except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
                continue
        return {
            "ok": False,
            "error": "未找到 Python，可以调用 install_python 安装",
        }

    def install_python(self) -> dict:
        """通过 winget 安装 Python 3.12（Windows 10/11 内置工具，无需管理员）"""
        import subprocess, sys as _sys
        _flags = subprocess.CREATE_NO_WINDOW if _sys.platform == "win32" else 0
        winget_args = [
            "winget", "install", "-e", "--id", "Python.Python.3.12",
            "--accept-package-agreements", "--accept-source-agreements",
            "--scope", "user",
        ]
        try:
            result = subprocess.run(
                winget_args,
                capture_output=True, text=True,
                timeout=300, encoding="utf-8", errors="replace",
                creationflags=_flags,
            )
            if result.returncode == 0:
                return {
                    "ok": True,
                    "method": "winget",
                    "output": (result.stdout or "")[-2000:],
                    "hint": "安装完成后请重启本程序使 PATH 生效",
                }
            return {
                "ok": False,
                "returncode": result.returncode,
                "error": (result.stderr or result.stdout or "")[-1000:],
                "fallback": "请手动前往 https://www.python.org/downloads/ 下载安装包",
            }
        except FileNotFoundError:
            return {
                "ok": False,
                "error": "winget 不可用（需 Windows 10 2004 及以上）",
                "fallback": "请手动前往 https://www.python.org/downloads/ 下载安装包",
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "安装超时（5 分钟），请检查网络或手动安装"}

    def run_python(
        self,
        script_rel: str,
        args: list | None = None,
        timeout: int = 120,
        stdin: str = "",
    ) -> dict:
        """在工作目录下运行 Python 脚本，返回 stdout/stderr/returncode。
        script_rel 也可以是工作目录下的相对路径；传入 None/'__inline__' 时配合 write_file 先把脚本写好再调用。
        """
        import subprocess
        try:
            script_path = self._resolve_read(script_rel)
        except PermissionError as e:
            return {"error": str(e)}
        if not script_path.exists():
            return {"error": f"脚本不存在: {script_rel}"}

        python_cmd = self._find_python()
        if python_cmd is None:
            return {"error": "未找到 Python，请先调用 check_python / install_python"}

        cmd = [python_cmd, str(script_path)] + list(args or [])
        import os as _os
        env = _os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        import sys as _sys
        _flags = subprocess.CREATE_NO_WINDOW if _sys.platform == "win32" else 0
        try:
            result = subprocess.run(
                cmd,
                input=stdin or None,
                capture_output=True, text=True,
                timeout=timeout,
                cwd=str(self.workspace),
                encoding="utf-8", errors="replace",
                env=env,
                creationflags=_flags,
            )
            return {
                "ok": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr[-2000:] if result.stderr else "",
            }
        except subprocess.TimeoutExpired:
            return {"error": f"运行超时（{timeout}s）"}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def run_shell(self, command: str, timeout: int = 60) -> dict:
        """在工作目录下执行任意 shell 命令（如 pip install、ffmpeg 转换等）。
        command 会经过 shell 解释，支持管道、环境变量等。
        """
        import subprocess, sys as _sys
        _flags = subprocess.CREATE_NO_WINDOW if _sys.platform == "win32" else 0
        try:
            result = subprocess.run(
                command, shell=True,
                capture_output=True, text=True,
                timeout=timeout,
                cwd=str(self.workspace),
                encoding="utf-8", errors="replace",
                creationflags=_flags,
            )
            return {
                "ok": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-2000:],
            }
        except subprocess.TimeoutExpired:
            return {"error": f"执行超时（{timeout}s）"}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def _find_python(self) -> str | None:
        """返回第一个可用的 python 命令名，找不到返回 None"""
        import subprocess, sys as _sys
        _flags = subprocess.CREATE_NO_WINDOW if _sys.platform == "win32" else 0
        for cmd in ["python", "python3", "py"]:
            try:
                r = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True, timeout=5,
                    creationflags=_flags,
                )
                if r.returncode == 0:
                    return cmd
            except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
                continue
        return None

    # ── 网络工具 ────────────────────────────────────────────

    def web_search(self, query: str, max_results: int = 8) -> dict:
        """用 DuckDuckGo 搜索，返回标题 + 摘要 + URL 列表"""
        try:
            from ddgs import DDGS
        except ImportError:
            return {"error": "ddgs 未安装，请先 run_shell 'pip install ddgs'"}
        try:
            with DDGS() as ddg:
                results = list(ddg.text(query, max_results=max_results))
            return {
                "ok": True,
                "count": len(results),
                "results": [
                    {"title": r.get("title", ""), "snippet": r.get("body", ""), "url": r.get("href", "")}
                    for r in results
                ],
            }
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def fetch_url(self, url: str, max_chars: int = 12000) -> dict:
        """抓取网页正文（自动过滤导航/广告），适合读文档、查规范"""
        try:
            import httpx
        except ImportError:
            return {"error": "httpx 未安装"}
        try:
            resp = httpx.get(
                url,
                follow_redirects=True,
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0 (compatible; LevelAssistant)"},
            )
            resp.raise_for_status()
        except Exception as e:
            return {"error": f"请求失败: {type(e).__name__}: {e}"}
        try:
            import trafilatura
            text = trafilatura.extract(resp.text) or resp.text[:max_chars]
        except Exception:
            text = resp.text
        return {"ok": True, "url": url, "content": text[:max_chars], "truncated": len(text) > max_chars}

    def download_file(self, url: str, dest_rel: str, timeout: int = 60) -> dict:
        """从 URL 下载文件到工作目录（二进制，支持图片/压缩包等）"""
        try:
            import httpx
        except ImportError:
            return {"error": "httpx 未安装"}
        try:
            dest = self._resolve_write(dest_rel)
        except PermissionError as e:
            return {"error": str(e)}
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with httpx.stream(
                "GET", url,
                follow_redirects=True, timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0 (compatible; LevelAssistant)"},
            ) as resp:
                resp.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in resp.iter_bytes(chunk_size=65536):
                        f.write(chunk)
        except Exception as e:
            return {"error": f"下载失败: {type(e).__name__}: {e}"}
        return {"ok": True, "dest": str(dest), "size": dest.stat().st_size}

    def http_request(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
        body: str | None = None,
        timeout: int = 30,
    ) -> dict:
        """发送任意 HTTP 请求，适合调用内部 REST API。body 传 JSON 字符串即可。"""
        try:
            import httpx
        except ImportError:
            return {"error": "httpx 未安装"}
        try:
            resp = httpx.request(
                method.upper(), url,
                headers=headers or {},
                content=body.encode() if body else None,
                follow_redirects=True,
                timeout=timeout,
            )
            text = resp.text
            return {
                "ok": resp.is_success,
                "status": resp.status_code,
                "headers": dict(resp.headers),
                "body": text[:8000],
                "truncated": len(text) > 8000,
            }
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    # ── 文件系统扩展 ─────────────────────────────────────────

    def move_file(self, src_rel: str, dst_rel: str) -> dict:
        """在工作目录内重命名或移动文件/目录（src 也可以是可读的绝对路径，但 dst 必须在工作目录）"""
        try:
            src = self._resolve_read(src_rel)
            dst = self._resolve_write(dst_rel)
        except PermissionError as e:
            return {"error": str(e)}
        if not src.exists():
            return {"error": f"源不存在: {src}"}
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return {"ok": True, "src": str(src), "dst": str(dst)}

    def make_dir(self, rel: str) -> dict:
        """在工作目录内创建目录（含所有中间层）"""
        try:
            p = self._resolve_write(rel)
        except PermissionError as e:
            return {"error": str(e)}
        p.mkdir(parents=True, exist_ok=True)
        return {"ok": True, "path": str(p)}

    def glob_files(self, pattern: str, dir_rel: str = ".") -> dict:
        """用通配符在目录下查找文件，如 '**/*.png' '*.json'。dir_rel 支持绝对路径（可读范围）。"""
        try:
            root = self._resolve_read(dir_rel)
        except PermissionError as e:
            return {"error": str(e)}
        if not root.exists():
            return {"error": f"目录不存在: {dir_rel}"}
        matches = [str(p) for p in root.glob(pattern)]
        matches.sort()
        return {"ok": True, "count": len(matches), "files": matches[:200]}

    def diff_files(self, a_rel: str, b_rel: str, context: int = 3) -> dict:
        """对比两个文本文件，返回 unified diff 格式的差异"""
        try:
            a = self._resolve_read(a_rel)
            b = self._resolve_read(b_rel)
        except PermissionError as e:
            return {"error": str(e)}
        for p, label in [(a, a_rel), (b, b_rel)]:
            if not p.exists():
                return {"error": f"不存在: {label}"}
        import difflib
        try:
            a_lines = a.read_text(encoding="utf-8").splitlines(keepends=True)
            b_lines = b.read_text(encoding="utf-8").splitlines(keepends=True)
        except Exception as e:
            return {"error": f"读取失败: {e}"}
        diff = list(difflib.unified_diff(a_lines, b_lines, fromfile=str(a), tofile=str(b), n=context))
        diff_text = "".join(diff)
        return {
            "ok": True,
            "changed": bool(diff),
            "diff": diff_text[:8000],
            "truncated": len(diff_text) > 8000,
        }

    # ── 图像信息 ─────────────────────────────────────────────

    def image_info(self, rel: str) -> dict:
        """获取图片的宽、高、格式、色彩模式。优先用 Pillow，没装则走内置解析。"""
        try:
            p = self._resolve_read(rel)
        except PermissionError as e:
            return {"error": str(e)}
        if not p.exists():
            return {"error": f"不存在: {p}"}
        try:
            from PIL import Image
            with Image.open(p) as img:
                return {
                    "ok": True,
                    "format": img.format,
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                    "size_bytes": p.stat().st_size,
                }
        except ImportError:
            pass
        except Exception as e:
            return {"error": f"Pillow 解析失败: {e}"}
        return self._image_info_builtin(p)

    def _image_info_builtin(self, p: Path) -> dict:
        """不依赖 Pillow 的简易图片头解析（PNG / JPEG）"""
        import struct
        data = p.read_bytes()
        size = len(data)
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", data[16:24])
            return {"ok": True, "format": "PNG", "width": w, "height": h, "size_bytes": size}
        if data[:2] == b"\xff\xd8":
            i = 2
            while i < size - 1:
                if data[i] != 0xff:
                    break
                marker = data[i + 1]
                if marker in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    return {"ok": True, "format": "JPEG", "width": w, "height": h, "size_bytes": size}
                seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
                i += 2 + seg_len
        return {"ok": True, "format": "unknown", "width": None, "height": None, "size_bytes": size}

    # ── 剪贴板 ───────────────────────────────────────────────

    def get_clipboard(self) -> dict:
        """读取系统剪贴板的文字内容"""
        import subprocess, sys as _sys
        _flags = subprocess.CREATE_NO_WINDOW if _sys.platform == "win32" else 0
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace",
                creationflags=_flags,
            )
            return {"ok": True, "text": result.stdout.rstrip("\r\n")}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def set_clipboard(self, text: str) -> dict:
        """把文字写入系统剪贴板"""
        import subprocess, sys as _sys
        _flags = subprocess.CREATE_NO_WINDOW if _sys.platform == "win32" else 0
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"Set-Clipboard -Value @'\n{text}\n'@"],
                timeout=10, check=True,
                creationflags=_flags,
            )
            return {"ok": True}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    # ── hetu_mcp：.ws 工作区专用工具 ─────────────────────────

    def _hetu_import(self):
        """把 hetu_mcp 目录加入 sys.path 并返回 (workspace_ops, validation_ops) 模块"""
        import sys
        from .config import mcp_dir
        mcp_root = mcp_dir() / "hetu_mcp"
        if not mcp_root.exists():
            raise FileNotFoundError(
                f"hetu_mcp 未找到，请确认 {mcp_root} 存在"
            )
        mcp_root_str = str(mcp_root)
        handlers_str = str(mcp_root / "handlers")
        for p in (mcp_root_str, handlers_str):
            if p not in sys.path:
                sys.path.insert(0, p)
        import importlib
        ws_ops = importlib.import_module("handlers.workspace_operations")
        val_ops = importlib.import_module("handlers.validation_operations")
        return ws_ops, val_ops

    def ws_load(self, file_path: str) -> dict:
        """读取并解析 .ws 文件，返回完整的 workspace JSON 数据。
        file_path 可以是绝对路径或工作目录下的相对路径。"""
        import asyncio
        try:
            p = self._resolve_read(file_path)
        except PermissionError as e:
            return {"error": str(e)}
        try:
            ws_ops, _ = self._hetu_import()
            result = asyncio.run(ws_ops.load_workspace_file(str(p)))
            return result
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def ws_save(self, file_path: str, content: dict, create_backup: bool = True) -> dict:
        """将 workspace JSON 写回 .ws 文件（仅限工作目录）。"""
        import asyncio
        try:
            p = self._resolve_write(file_path)
        except PermissionError as e:
            return {"error": str(e)}
        try:
            ws_ops, _ = self._hetu_import()
            result = asyncio.run(ws_ops.save_workspace_file(str(p), content, None, create_backup))
            return {"ok": True, "result": result}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def ws_get_fragments(self, workspace_data: dict) -> dict:
        """列出 BlockScript / 整个 .ws 中所有 fragment 的摘要（头部 define + 位置）。"""
        try:
            ws_ops, _ = self._hetu_import()
            result = ws_ops.get_fragments(workspace_data)
            return {"ok": True, "fragments": result}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def ws_add_fragment(self, file_path: str, fragment: dict,
                        script_id: str | None = None) -> dict:
        """向 .ws 文件的指定 BlockScript 追加一个 fragment（直接读写文件，返回 diff 摘要）。"""
        try:
            p = self._resolve_write(file_path)
        except PermissionError as e:
            return {"error": str(e)}
        try:
            ws_ops, _ = self._hetu_import()
            result = ws_ops.add_fragment_to_file(str(p), fragment, script_id, None)
            return result
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def ws_remove_fragment(self, file_path: str, fragment_index: int,
                           script_id: str | None = None) -> dict:
        """从 .ws 文件的 BlockScript 删除指定 index 的 fragment（直接读写文件）。"""
        try:
            p = self._resolve_write(file_path)
        except PermissionError as e:
            return {"error": str(e)}
        try:
            ws_ops, _ = self._hetu_import()
            result = ws_ops.remove_fragment_to_file(str(p), fragment_index, script_id, None)
            return result
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def ws_validate(self, file_path: str) -> dict:
        """校验 .ws 文件的结构合法性（check no-NEXT, valid blocks 等）。
        直接传文件路径，工具内部自动加载再验证，不需要手动传 workspace_data。
        """
        import asyncio
        try:
            ws_ops, val_ops = self._hetu_import()
            p = self._resolve_read(file_path)
            result = ws_ops.load_workspace_file(str(p))
            if asyncio.iscoroutine(result):
                result = asyncio.run(result)
            data = result.get("data") or result
            val_result = val_ops.validate_workspace(data)
            if asyncio.iscoroutine(val_result):
                val_result = asyncio.run(val_result)
            return val_result
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def ws_find_blocks(self, workspace_data: dict, block_define: str) -> dict:
        """在整个 workspace 中按 define 名称查找所有 block（如 'Repeat'、'BroadcastMessage'）。"""
        try:
            _, val_ops = self._hetu_import()
            result = val_ops.find_blocks_by_type(workspace_data, block_define)
            return {"ok": True, "results": result}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def ws_get_block_doc(self, block_define: str) -> dict:
        """获取某个 block define 的文档（参数说明、用途）。"""
        try:
            _, val_ops = self._hetu_import()
            doc = val_ops.get_block_documentation(block_define)
            return {"ok": True, "doc": doc}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def ws_stats(self, workspace_data: dict) -> dict:
        """分析 workspace 统计信息：fragment 数、block 数、myblock 数等。"""
        try:
            _, val_ops = self._hetu_import()
            result = val_ops.analyze_workspace_statistics(workspace_data)
            return result
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def ws_create_myblock(self, file_path: str, name: str, display_name: str,
                          parameters: list | None = None, script_id: str | None = None) -> dict:
        """在 .ws 文件中创建一个 myblock 定义（直接读写文件，返回含 auto-generated myblock_name 的 diff）。"""
        try:
            p = self._resolve_write(file_path)
        except PermissionError as e:
            return {"error": str(e)}
        try:
            ws_ops, _ = self._hetu_import()
            result = ws_ops.create_myblock_to_file(
                str(p), name, display_name, parameters or [], True, script_id, None
            )
            return result
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    def ws_get_value(self, file_path: str, json_path: str) -> dict:
        """从 .ws 文件中按 JSON 路径读取某个值，方便 AI 在修改前先确认当前内容。
        json_path 使用 . 分隔，数字代表数组索引。
        例如：
          "scene.props2.errMsg.value"
          "scene.children.6.children.0.fragments.2.head.sections.0.params.0.val"
        """
        import json as _json
        try:
            p = self._resolve_read(file_path)
        except PermissionError as e:
            return {"error": str(e)}
        if not p.exists():
            return {"error": f"文件不存在: {file_path}"}
        try:
            data = _json.loads(p.read_bytes().decode("utf-8"))
        except Exception as e:
            return {"error": f"读取失败: {e}"}
        parts = json_path.split(".")
        node = data
        try:
            for part in parts:
                node = node[int(part)] if isinstance(node, list) else node[part]
        except (KeyError, IndexError, TypeError, ValueError) as e:
            return {"error": f"路径 '{json_path}' 无效: {e}"}
        return {"ok": True, "path": json_path, "value": node}

    def ws_set_value(self, file_path: str, json_path: str, value) -> dict:
        """在 .ws 文件中按 JSON 路径精准修改一个值，无需加载整个 JSON 再保存。
        json_path 使用 . 分隔键，数字代表数组索引。
        例如：
          "scene.props2.errMsg.value"  → 修改 scene.props2.errMsg.value
          "scene.children.6.children.0.fragments.2.head.sections.0.params.0.val"
        修改后会自动更新文件 modified 时间戳，并保持 JSON 紧凑格式（与原始格式一致）。
        """
        import json as _json
        try:
            p = self._resolve_write(file_path)
        except PermissionError as e:
            return {"error": str(e)}
        if not p.exists():
            return {"error": f"文件不存在: {file_path}"}
        try:
            data = _json.loads(p.read_bytes().decode("utf-8"))
        except Exception as e:
            return {"error": f"读取失败: {e}"}

        parts = json_path.split(".")
        node = data
        try:
            for part in parts[:-1]:
                node = node[int(part)] if isinstance(node, list) else node[part]
            last = parts[-1]
            old_value = node[int(last)] if isinstance(node, list) else node.get(last)
            if isinstance(node, list):
                node[int(last)] = value
            else:
                node[last] = value
        except (KeyError, IndexError, TypeError, ValueError) as e:
            return {"error": f"路径 '{json_path}' 无效: {e}"}

        try:
            p.write_text(_json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        except Exception as e:
            return {"error": f"写入失败: {e}"}
        return {"ok": True, "path": json_path, "old": old_value, "new": value}

    def ws_find_value(self, file_path: str, search_value: str, max_results: int = 20) -> dict:
        """在 .ws 文件中递归搜索某个字符串值，返回所有匹配的 JSON 路径。
        用于在不知道确切路径的情况下，先找到值的位置，再用 ws_set_value 修改。
        search_value 为字符串，会与节点的字符串表示做包含匹配。
        """
        import json as _json
        try:
            p = self._resolve_read(file_path)
        except PermissionError as e:
            return {"error": str(e)}
        if not p.exists():
            return {"error": f"文件不存在: {file_path}"}
        try:
            data = _json.loads(p.read_bytes().decode("utf-8"))
        except Exception as e:
            return {"error": f"读取失败: {e}"}

        results = []

        def _search(node, path: str):
            if len(results) >= max_results:
                return
            if isinstance(node, dict):
                for k, v in node.items():
                    _search(v, f"{path}.{k}" if path else k)
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    _search(v, f"{path}.{i}" if path else str(i))
            elif isinstance(node, str) and search_value in node:
                results.append({"path": path, "value": node})

        _search(data, "")
        return {"ok": True, "count": len(results), "results": results}


    def pause_and_ask(self, question: str, context: str = "") -> dict:
        """[子 agent 专用] 遇到 MCP 失败或需要主 agent 决策时调用，暂停执行并上报问题。
        调用后子 agent 应立即停止（不再调用其他工具）。
        主 agent 收到 paused=True 的结果后，通过 resume_subagent 注入指示并恢复执行。
        question: 需要主 agent 回答的问题（含失败工具名、报错信息、可能的处理方案）
        context: 当前执行进度（已完成哪些改动、卡在第几步）
        """
        # 此方法在 _run_subagent_loop 里被拦截，不会真正执行到这里。
        # 若主 agent 误调（不在子 agent 内部），返回明确错误。
        return {"error": "pause_and_ask 只能在子 agent 内部使用（需通过 run_subagent 启动）"}

    def _run_subagent_loop(
        self,
        system: str,
        messages: list,
        client,
        tools: list,
        max_iterations: int = 30,
    ) -> dict:
        """子 agent 核心执行循环（run_subagent / resume_subagent 共用）。
        支持 pause_and_ask：检测到该工具调用时，序列化对话历史到工作目录，
        返回 {"ok": True, "paused": True, "resume_id": ..., "question": ...}。
        """
        from .config import DEFAULT_MODEL as _DEFAULT_MODEL
        import json as _json
        import uuid as _uuid
        import re as _re

        full_text: list[str] = []

        for _ in range(max_iterations):
            try:
                with client.messages.stream(
                    model=_DEFAULT_MODEL,
                    max_tokens=8000,
                    system=system,
                    tools=tools,
                    messages=messages,
                ) as stream:
                    for event in stream:
                        etype = getattr(event, "type", "")
                        if etype == "content_block_delta":
                            delta = getattr(event, "delta", None)
                            if delta and delta.type == "text_delta":
                                full_text.append(delta.text)
                    resp = stream.get_final_message()
            except Exception as e:
                return {"ok": False, "error": f"子 Agent 请求失败: {e}"}

            stop_reason = resp.stop_reason
            assistant_blocks = []
            for block in resp.content:
                if block.type == "text":
                    assistant_blocks.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_blocks.append({
                        "type": "tool_use", "id": block.id,
                        "name": block.name, "input": block.input,
                    })
            messages.append({"role": "assistant", "content": assistant_blocks})

            if stop_reason != "tool_use":
                break

            # ── 检查是否有 pause_and_ask 调用 ──────────────────────────────
            pause_block = next(
                (b for b in resp.content
                 if b.type == "tool_use" and b.name == "pause_and_ask"),
                None,
            )
            if pause_block:
                resume_id = str(_uuid.uuid4())[:8]
                state = {
                    "system": system,
                    "messages": messages,       # 包含本轮 assistant 消息（含 pause_and_ask tool_use）
                    "tool_use_id": pause_block.id,
                }
                state_file = self.workspace / f".pause_state_{resume_id}.json"
                state_file.write_text(
                    _json.dumps(state, ensure_ascii=False), encoding="utf-8"
                )
                return {
                    "ok": True,
                    "paused": True,
                    "resume_id": resume_id,
                    "question": pause_block.input.get("question", ""),
                    "context": pause_block.input.get("context", ""),
                }

            # ── 普通工具调用 ───────────────────────────────────────────────
            tool_results = []
            for block in resp.content:
                if block.type != "tool_use":
                    continue
                try:
                    method = getattr(self, block.name, None)
                    result = method(**block.input) if method else {"error": f"未知工具: {block.name}"}
                except Exception as e:
                    result = {"error": f"{type(e).__name__}: {e}"}
                try:
                    content = _json.dumps(result, ensure_ascii=False)
                except Exception:
                    content = str(result)
                if len(content) > 60000:
                    content = content[:60000] + "...[截断]"
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": content,
                })
            messages.append({"role": "user", "content": tool_results})

        output = "".join(full_text).strip()

        # 兜底：流式捕获文字过短时，从最后一条 assistant 消息捞文本
        if len(output) < 100 and messages and messages[-1]["role"] == "assistant":
            last_texts = [
                b["text"] for b in messages[-1]["content"]
                if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip()
            ]
            if last_texts:
                fallback = "\n".join(last_texts).strip()
                if len(fallback) > len(output):
                    output = fallback

        result: dict = {"ok": True, "output": output, "output_length": len(output)}

        # 审查员 FAIL 检测
        _FAIL_PATTERNS = [
            r"总体[：:]\s*FAIL",
            r"总体判定[：:]\s*FAIL",
            r"\bFAIL\b.*总体",
        ]
        if any(_re.search(p, output) for p in _FAIL_PATTERNS):
            result["reviewer_fail"] = True
            result["system_warning"] = (
                "⛔ [系统强制] 审查员返回 FAIL。"
                "按 level-modify/SKILL.md 第4步，必须新开改造员 → 新开审查员，"
                "不允许自行宣判「可豁免」。"
                "如需跳过某条 FAIL，必须先向用户说明原因并获得明确 OK。"
            )
        return result

    def run_subagent(
        self,
        task: str,
        context: str = "",
        max_iterations: int = 30,
    ) -> dict:
        """启动一个独立子 Agent 完成指定子任务，返回其最终文字输出。
        子 Agent 与主 Agent 共享同一工作目录和可读根目录，但上下文完全隔离。
        适合将复杂任务拆分为：分析子任务 / 修改子任务 / 校验子任务等。

        若子 Agent 调用 pause_and_ask，返回：
          {"ok": True, "paused": True, "resume_id": "...", "question": "..."}
        主 Agent 决策后调用 resume_subagent(resume_id, instruction) 继续。
        """
        from .config import (
            ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL, CLAUDE_USER_AGENT,
            DEFAULT_MODEL, output_dir, skills_dir, cursor_skills_dir, mcp_dir,
        )
        import anthropic as _anthropic

        system = "\n".join([
            "你是一个专注执行子任务的 Agent，由主 Agent 启动。",
            "",
            "## 强制规则（违反 = 任务失败）",
            "1. 所有工具调用结束后，**最后一条消息必须是纯文字**，包含完整的结构化结论（Markdown 格式）。",
            "2. 不允许以工具调用结束任务——必须在最终 end_turn 消息里输出结论。",
            "3. 不需要打包，不需要向用户确认，只需输出结论文字。",
            "4. 如果脚本/工具输出了数据，必须将关键数据整理后写入最终回复，不能只说「已完成」。",
            "5. **遇到 MCP 工具失败、或无法自行决策时**：调用 `pause_and_ask` 工具（说明问题和当前进度），"
            "   然后立即停止（不再调用其他工具）。主 Agent 会通过 `resume_subagent` 提供指示后恢复执行。",
            "",
            "## 路径",
            f"- 工作目录：`{self.workspace}`",
            f"- 产出目录：`{output_dir()}`",
            f"- Skill 目录：`{cursor_skills_dir()}`",
            f"- MCP 目录：`{mcp_dir()}`",
            f"- 公共资源目录：`{skills_dir()}`",
        ])

        user_content = f"{context}\n\n{task}".strip() if context else task
        messages: list = [{"role": "user", "content": user_content}]

        client = _anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY,
            base_url=ANTHROPIC_BASE_URL,
            default_headers={"User-Agent": CLAUDE_USER_AGENT},
        )
        # 子 agent 不能递归调用 run_subagent / run_subagents_parallel / resume_subagent
        _SUBAGENT_BLOCKED = {"run_subagent", "run_subagents_parallel", "resume_subagent"}
        tools = [t for t in tool_definitions() if t["name"] not in _SUBAGENT_BLOCKED]

        return self._run_subagent_loop(system, messages, client, tools, max_iterations)

    def resume_subagent(self, resume_id: str, instruction: str) -> dict:
        """恢复一个因 pause_and_ask 暂停的子 Agent，注入主 Agent 指示后继续执行。
        resume_id : run_subagent 返回结果中的 resume_id 字段。
        instruction: 主 Agent 的指示（直接回答子 agent 的问题，说明如何处理）。
        """
        from .config import (
            ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL, CLAUDE_USER_AGENT,
        )
        import anthropic as _anthropic
        import json as _json

        state_file = self.workspace / f".pause_state_{resume_id}.json"
        if not state_file.exists():
            return {"error": f"暂停状态不存在：resume_id={resume_id}（文件 .pause_state_{resume_id}.json 未找到）"}

        state = _json.loads(state_file.read_text(encoding="utf-8"))
        state_file.unlink()  # 用完即删，避免残留

        system = state["system"]
        messages = state["messages"]
        tool_use_id = state["tool_use_id"]

        # 将主 Agent 的指示作为 pause_and_ask 的工具结果注入
        messages.append({
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": f"[主 Agent 指示] {instruction}",
            }],
        })

        client = _anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY,
            base_url=ANTHROPIC_BASE_URL,
            default_headers={"User-Agent": CLAUDE_USER_AGENT},
        )
        _SUBAGENT_BLOCKED = {"run_subagent", "run_subagents_parallel", "resume_subagent"}
        tools = [t for t in tool_definitions() if t["name"] not in _SUBAGENT_BLOCKED]

        return self._run_subagent_loop(system, messages, client, tools, max_iterations=30)

    def run_subagents_parallel(
        self,
        tasks: list,
        max_iterations: int = 30,
    ) -> dict:
        """并行启动多个独立子 Agent，每个子任务在独立线程中同时执行，所有任务完成后汇总返回。
        tasks 为 list of {"task": str, "context"?: str}。
        适合资源搜索等需要同时查询多个独立数据源的场景。
        """
        import concurrent.futures as _cf
        import json as _json
        import re as _re
        from .config import cursor_skills_dir as _cursor_skills_dir

        # 兼容 AI 传入 JSON 字符串的情况（全程静默转换，永不向 AI 报错）
        if isinstance(tasks, str):
            parsed = None

            # 策略1：标准 json.loads
            try:
                parsed = _json.loads(tasks)
            except Exception:
                pass

            # 策略2：ast.literal_eval（处理 Python list / 单引号语法）
            if parsed is None:
                try:
                    import ast as _ast
                    parsed = _ast.literal_eval(tasks)
                except Exception:
                    pass

            # 策略3：宽容 JSON——把全/半角引号统一化后再解析
            if parsed is None:
                try:
                    fixed = (tasks
                             .replace('\u201c', '"').replace('\u201d', '"')   # 中文弯引号
                             .replace('\u2018', "'").replace('\u2019', "'"))  # 中文单引号
                    parsed = _json.loads(fixed)
                except Exception:
                    pass

            # 策略4：正则逐段提取 {"task": "..."} 对象
            # 用贪婪跨行匹配，对 task 值内含未转义引号的情况做宽松处理
            if parsed is None:
                try:
                    # 找到所有 {...} 块，每块内用 'task' key 提取值
                    objects: list = []
                    for blk in _re.findall(r'\{[^{}]*\}', tasks, _re.DOTALL):
                        # task 值：从 "task": " 到 下一个 ", 或 行尾
                        m = _re.search(r'"task"\s*:\s*"(.*?)"(?:\s*[,}])', blk, _re.DOTALL)
                        if m:
                            obj: dict = {"task": m.group(1).replace('\\n', '\n').replace('\\"', '"')}
                            ctx = _re.search(r'"context"\s*:\s*"(.*?)"(?:\s*[,}])', blk, _re.DOTALL)
                            if ctx:
                                obj["context"] = ctx.group(1).replace('\\n', '\n').replace('\\"', '"')
                            objects.append(obj)
                    if objects:
                        parsed = objects
                except Exception:
                    pass

            # 所有策略都失败：仅作最后保障，理论上不应到达
            if parsed is None:
                return {"ok": False, "error": "tasks 参数解析失败，请直接传入 array 而非 JSON 字符串"}
            tasks = parsed

        if not tasks:
            return {"ok": True, "count": 0, "results": [], "combined_output": ""}

        # 自动预注入技能文件：检测 .cursor/skills/*/SKILL.md 引用，直接把内容嵌进 prompt，
        # 省去子 Agent 读文件的一轮 API 调用（约 10-15 秒）
        _skill_cache: dict = {}

        def _inject_skill(task_str: str) -> str:
            pattern = (
                r'首先读取你的技能文件：\s*\n\n`(\.cursor/skills/[^`]+/SKILL\.md)`\s*\n\n读完后，'
            )

            def _replace(m: "_re.Match") -> str:
                rel = m.group(1)  # e.g. .cursor/skills/resource-search/SKILL.md
                if rel not in _skill_cache:
                    # rel 以 .cursor/skills/ 开头，cursor_skills_dir() 即是该前缀对应的目录
                    sub = rel[len(".cursor/skills/"):]  # e.g. resource-search/SKILL.md
                    skill_path = _cursor_skills_dir() / sub
                    try:
                        _skill_cache[rel] = skill_path.read_text(encoding="utf-8")
                    except Exception:
                        _skill_cache[rel] = None
                content = _skill_cache.get(rel)
                if content:
                    return (
                        "你的技能规范已预加载如下（无需读取文件，直接按规范执行）：\n\n"
                        f"<skill_spec>\n{content}\n</skill_spec>\n\n"
                        "按照上述规范，"
                    )
                return m.group(0)  # 找不到文件则保持原样

            return _re.sub(pattern, _replace, task_str, flags=_re.DOTALL)

        def _run_one(idx_task):
            idx, task_dict = idx_task
            task_str = _inject_skill(task_dict.get("task", ""))
            ctx = task_dict.get("context", "")
            result = self.run_subagent(
                task=task_str, context=ctx, max_iterations=max_iterations
            )
            return idx, result

        n = len(tasks)
        results: list = [None] * n
        with _cf.ThreadPoolExecutor(max_workers=min(n, 8)) as executor:
            futures = {
                executor.submit(_run_one, (i, t)): i for i, t in enumerate(tasks)
            }
            for future in _cf.as_completed(futures):
                try:
                    idx, result = future.result()
                    results[idx] = result
                except Exception as e:
                    idx = futures[future]
                    results[idx] = {"ok": False, "error": str(e)}

        all_ok = all(r and r.get("ok") for r in results)
        outputs = [r.get("output", "") if r else "" for r in results]
        combined = "\n\n---\n\n".join(
            f"【子任务 {i + 1}】\n{o}" for i, o in enumerate(outputs) if o
        )
        ret: dict = {
            "ok": all_ok,
            "count": n,
            "results": results,
            "combined_output": combined,
        }

        # 硬约束③：检测子任务"未找到"结果，注入强制警告防止主 Agent 编造 AssetId
        _not_found_patterns = ["未找到", "没有找到", "无法找到", "not found", "无匹配"]
        not_found_tasks = [
            f"子任务 {i + 1}"
            for i, o in enumerate(outputs)
            if o and any(p in o for p in _not_found_patterns)
        ]
        if not_found_tasks:
            ret["system_warning"] = (
                f"⛔ [系统强制] {', '.join(not_found_tasks)} 明确返回「未找到」。"
                "按 resource-search-main/SKILL.md 约束③，"
                "必须如实告知用户哪些资源未找到，"
                "严禁在资源清单中补充或编造任何 AssetId。"
            )

        return ret


def tool_definitions() -> list:
    return [
        {
            "name": "extract_archive",
            "description": "解压压缩包。archive_path 可以是绝对路径（用户上传的文件），dest 是工作目录下的子目录名。支持 zip/tar/tar.gz/7z。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "archive_path": {"type": "string"},
                    "dest": {"type": "string", "description": "工作目录下的子目录，默认 extracted"},
                },
                "required": ["archive_path"],
            },
        },
        {
            "name": "list_dir",
            "description": "列目录。rel 可以是工作目录下的相对路径，也可以是技能目录或上传文件的绝对路径。",
            "input_schema": {
                "type": "object",
                "properties": {"rel": {"type": "string", "description": "默认 '.'"}},
            },
        },
        {
            "name": "read_file",
            "description": "读文件。rel 支持相对路径（工作目录）或绝对路径（技能目录/上传文件）。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "rel": {"type": "string"},
                    "max_chars": {"type": "integer", "default": 8000},
                },
                "required": ["rel"],
            },
        },
        {
            "name": "write_file",
            "description": "写入/覆盖文件，仅限工作目录内。",
            "input_schema": {
                "type": "object",
                "properties": {"rel": {"type": "string"}, "content": {"type": "string"}},
                "required": ["rel", "content"],
            },
        },
        {
            "name": "replace_in_file",
            "description": "在工作目录内某文件做字符串替换。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "rel": {"type": "string"},
                    "old": {"type": "string"},
                    "new": {"type": "string"},
                },
                "required": ["rel", "old", "new"],
            },
        },
        {
            "name": "copy_file",
            "description": "复制文件到工作目录。src_external 可以是绝对路径（上传文件/技能目录内的参考素材），dest_rel 必须在工作目录下。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "src_external": {"type": "string"},
                    "dest_rel": {"type": "string"},
                },
                "required": ["src_external", "dest_rel"],
            },
        },
        {
            "name": "grep_file",
            "description": (
                "在单个文件中用正则表达式逐行搜索，等价于 `rg <pattern> <file>`。"
                "专为搜索大型 JSONL / Markdown 资源索引文件设计，无需安装 ripgrep。"
                "file_rel 可以是绝对路径或相对于工作目录/技能目录的相对路径。"
                "当需要在 resource_index.jsonl / asset_catalog.md 等大文件中精准过滤时，"
                "优先使用本工具而不是 run_shell('rg ...')。"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Python 正则表达式，如 '\"emotions\".*\"开心\"'"},
                    "file_rel": {"type": "string", "description": "文件路径（绝对或相对均可）"},
                    "max_hits": {"type": "integer", "description": "最多返回行数，默认 200", "default": 200},
                    "ignore_case": {"type": "boolean", "description": "是否忽略大小写，默认 false", "default": False},
                },
                "required": ["pattern", "file_rel"],
            },
        },
        {
            "name": "search_in_files",
            "description": "在目录中搜索包含指定字符串的行。dir_rel 可以是工作/技能/上传目录的路径。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "dir_rel": {"type": "string", "default": "."},
                    "max_hits": {"type": "integer", "default": 50},
                },
                "required": ["pattern"],
            },
        },
        {
            "name": "create_archive",
            "description": "把工作目录下的子目录打成 zip，放在工作目录根。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "src_dir": {"type": "string"},
                    "output_name": {"type": "string", "default": "output.zip"},
                },
                "required": ["src_dir"],
            },
        },
        {
            "name": "delete_path",
            "description": "删除工作目录下的文件或目录。",
            "input_schema": {
                "type": "object",
                "properties": {"rel": {"type": "string"}},
                "required": ["rel"],
            },
        },
        {
            "name": "check_python",
            "description": "检测系统是否安装了 Python，返回可用的命令和版本号。在调用 run_python 前应先确认 Python 存在。",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "install_python",
            "description": "通过 winget 在 Windows 上安装 Python 3.12（用户级安装，无需管理员权限）。仅在 check_python 返回未找到时调用。安装后须提示用户重启程序。",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "run_python",
            "description": (
                "在工作目录下运行一个 Python 脚本（用 write_file 先把脚本写好）。"
                "返回 stdout / stderr / returncode。"
                "timeout 默认 120 秒，可按需调大。"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "script_rel": {
                        "type": "string",
                        "description": "工作目录下脚本的相对路径，如 process.py",
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "命令行参数列表，可省略",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "超时秒数，默认 120",
                    },
                    "stdin": {
                        "type": "string",
                        "description": "可选的标准输入字符串",
                    },
                },
                "required": ["script_rel"],
            },
        },
        {
            "name": "run_shell",
            "description": (
                "在工作目录下执行任意 shell 命令（支持 pip install、ffmpeg 等）。"
                "返回 stdout / stderr / returncode。timeout 默认 60 秒。"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要执行的 shell 命令"},
                    "timeout": {"type": "integer", "description": "超时秒数，默认 60"},
                },
                "required": ["command"],
            },
        },
        # ── 网络工具 ─────────────────────────────────────────
        {
            "name": "web_search",
            "description": "用 DuckDuckGo 搜索网页，返回标题、摘要和 URL 列表。适合查资料、找解决方案、查规范文档。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "description": "返回条数，默认 8"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "fetch_url",
            "description": "抓取网页正文（自动过滤导航/广告），适合读文档、查规范详情。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "max_chars": {"type": "integer", "description": "最多返回字符数，默认 12000"},
                },
                "required": ["url"],
            },
        },
        {
            "name": "download_file",
            "description": "从 URL 下载文件（图片/压缩包/二进制均可）到工作目录。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "dest_rel": {"type": "string", "description": "工作目录下的目标路径"},
                    "timeout": {"type": "integer", "description": "超时秒数，默认 60"},
                },
                "required": ["url", "dest_rel"],
            },
        },
        {
            "name": "http_request",
            "description": "发送任意 HTTP 请求（GET/POST/PUT/DELETE），适合调用内部 REST API 或第三方接口。body 传 JSON 字符串。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "description": "GET / POST / PUT / DELETE 等"},
                    "url": {"type": "string"},
                    "headers": {"type": "object", "description": "请求头键值对"},
                    "body": {"type": "string", "description": "请求体，JSON 字符串"},
                    "timeout": {"type": "integer", "description": "超时秒数，默认 30"},
                },
                "required": ["method", "url"],
            },
        },
        # ── 文件系统扩展 ──────────────────────────────────────
        {
            "name": "move_file",
            "description": "重命名或移动文件/目录。src_rel 支持可读路径，dst_rel 必须在工作目录内。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "src_rel": {"type": "string"},
                    "dst_rel": {"type": "string"},
                },
                "required": ["src_rel", "dst_rel"],
            },
        },
        {
            "name": "make_dir",
            "description": "在工作目录内创建目录（含所有中间层）。",
            "input_schema": {
                "type": "object",
                "properties": {"rel": {"type": "string"}},
                "required": ["rel"],
            },
        },
        {
            "name": "glob_files",
            "description": "用通配符查找文件，如 '**/*.png'、'config/*.json'。dir_rel 支持绝对路径（可读范围内）。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "glob 模式，如 **/*.png"},
                    "dir_rel": {"type": "string", "description": "搜索根目录，默认工作目录 '.'"},
                },
                "required": ["pattern"],
            },
        },
        {
            "name": "diff_files",
            "description": "对比两个文本文件，返回 unified diff 格式的差异，用于验证修改结果。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "a_rel": {"type": "string", "description": "原始文件路径"},
                    "b_rel": {"type": "string", "description": "修改后文件路径"},
                    "context": {"type": "integer", "description": "上下文行数，默认 3"},
                },
                "required": ["a_rel", "b_rel"],
            },
        },
        # ── 图像 ──────────────────────────────────────────────
        {
            "name": "image_info",
            "description": "获取图片的宽、高、格式、色彩模式和文件大小。支持 PNG/JPEG，装了 Pillow 则支持更多格式。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "rel": {"type": "string", "description": "图片路径，支持相对或绝对路径（可读范围）"},
                },
                "required": ["rel"],
            },
        },
        # ── 剪贴板 ────────────────────────────────────────────
        {
            "name": "get_clipboard",
            "description": "读取系统剪贴板的文字内容，方便用户把外部内容传入任务。",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "set_clipboard",
            "description": "把文字写入系统剪贴板，方便用户直接粘贴 AI 生成的内容到其他软件。",
            "input_schema": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
        # ── hetu_mcp：.ws 工作区专用工具 ─────────────────────────
        {
            "name": "ws_load",
            "description": "读取并解析 .ws 文件，返回完整的 workspace JSON。优先用此工具代替 read_file 读 .ws 文件。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": ".ws 文件的绝对路径或相对于工作目录的路径"},
                },
                "required": ["file_path"],
            },
        },
        {
            "name": "ws_save",
            "description": "将修改后的 workspace JSON 写回 .ws 文件（仅限工作目录）。支持自动备份。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "content": {"type": "object", "description": "完整的 workspace JSON 对象"},
                    "create_backup": {"type": "boolean", "description": "是否自动备份，默认 true"},
                },
                "required": ["file_path", "content"],
            },
        },
        {
            "name": "ws_get_fragments",
            "description": "列出 BlockScript / 整个 .ws 中所有 fragment（头部 define 名称 + 位置）。需先 ws_load 拿到 workspace_data。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "workspace_data": {"type": "object", "description": "ws_load 返回的 data 字段"},
                },
                "required": ["workspace_data"],
            },
        },
        {
            "name": "ws_add_fragment",
            "description": "向 .ws 文件的 BlockScript 追加一个 fragment，直接读写文件，返回 diff 摘要。fragment 需包含 pos 和 head。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "fragment": {"type": "object", "description": "含 pos([x,y] 字符串数组) 和 head(block) 的 fragment 对象"},
                    "script_id": {"type": "string", "description": "多脚本 workspace 时指定目标 script id"},
                },
                "required": ["file_path", "fragment"],
            },
        },
        {
            "name": "ws_remove_fragment",
            "description": "从 .ws 文件的 BlockScript 删除指定索引的 fragment，直接读写文件，返回 diff 摘要。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "fragment_index": {"type": "integer", "description": "要删除的 fragment 索引（从 ws_get_fragments 结果获取）"},
                    "script_id": {"type": "string"},
                },
                "required": ["file_path", "fragment_index"],
            },
        },
        {
            "name": "ws_validate",
            "description": "校验 .ws 文件的结构合法性（无非法 next 链、block 结构正确等）。改完 .ws 后必须调用。直接传文件路径，不需要传 workspace_data。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": ".ws 文件路径（相对工作目录或绝对路径）"},
                },
                "required": ["file_path"],
            },
        },
        {
            "name": "ws_find_blocks",
            "description": "在整个 workspace 中按 define 名称查找所有 block，如 'Repeat'、'BroadcastMessage'、'SetVar'。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "workspace_data": {"type": "object"},
                    "block_define": {"type": "string", "description": "block 的 define 名称"},
                },
                "required": ["workspace_data", "block_define"],
            },
        },
        {
            "name": "ws_get_block_doc",
            "description": "获取某个 block define 的文档（参数说明、类型、用途）。不确定某个 block 怎么用时先查这个。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "block_define": {"type": "string"},
                },
                "required": ["block_define"],
            },
        },
        {
            "name": "ws_stats",
            "description": "分析 workspace 统计信息：fragment 数、block 总数、myblock 数、各 define 频率等。用于快速了解关卡规模。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "workspace_data": {"type": "object"},
                },
                "required": ["workspace_data"],
            },
        },
        {
            "name": "ws_create_myblock",
            "description": "在 .ws 文件中创建一个 myblock 定义，直接读写文件，返回含自动生成的 myblock_name 的 diff。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "name": {"type": "string", "description": "myblock 内部名称（英文）"},
                    "display_name": {"type": "string", "description": "myblock 显示名称"},
                    "parameters": {"type": "array", "description": "参数定义列表"},
                    "script_id": {"type": "string"},
                },
                "required": ["file_path", "name", "display_name"],
            },
        },
        {
            "name": "ws_get_value",
            "description": "从 .ws 文件按 JSON 路径读取指定值。先用 ws_find_value 找到路径，再用此工具确认值后，才调用 ws_set_value 修改。",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "json_path": {
                        "type": "string",
                        "description": "用 . 分隔的 JSON 路径，数字代表数组索引。如：scene.props2.errMsg.value",
                    },
                },
                "required": ["file_path", "json_path"],
            },
        },
        {
            "name": "ws_set_value",
            "description": (
                "在 .ws 文件中按 JSON 路径精准修改一个值，避免写 Python 脚本。"
                "修改前必须先用 ws_get_value 确认旧值。"
                "json_path 用 . 分隔，数字代表数组索引。"
                "例如：scene.children.6.children.0.fragments.2.head.sections.0.params.0.val"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "json_path": {"type": "string", "description": "同 ws_get_value 的路径格式"},
                    "value": {
                        "description": "要写入的新值",
                        "oneOf": [
                            {"type": "string"},
                            {"type": "number"},
                            {"type": "boolean"},
                            {"type": "array"},
                            {"type": "object"},
                            {"type": "null"},
                        ],
                    },
                },
                "required": ["file_path", "json_path", "value"],
            },
        },
        {
            "name": "ws_find_value",
            "description": (
                "在 .ws 文件中递归搜索包含指定字符串的值，返回所有匹配的 JSON 路径。"
                "当不知道某个值在哪里时先用此工具找路径，再用 ws_get_value 确认，最后用 ws_set_value 修改。"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "search_value": {"type": "string", "description": "要搜索的字符串（支持部分匹配）"},
                    "max_results": {"type": "integer", "description": "最多返回结果数，默认 20"},
                },
                "required": ["file_path", "search_value"],
            },
        },
        {
            "name": "run_subagent",
            "description": (
                "启动一个独立子 Agent 完成指定子任务，返回其最终输出。"
                "子 Agent 与主 Agent 共享工作目录，上下文完全隔离，拥有全部工具能力（ws_*、run_python 等）。"
                "适用场景：把复杂任务拆分，例如让子 Agent 专门分析关卡结构，或专门执行某一段修改，主 Agent 汇总结果。"
                "禁止在子 Agent 里再次调用 run_subagent（防止递归）。"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "子任务描述，越具体越好，包含需要读取的文件路径和期望的输出格式",
                    },
                    "context": {
                        "type": "string",
                        "description": "传给子 Agent 的背景信息，例如主 Agent 已完成的分析结论",
                    },
                    "max_iterations": {
                        "type": "integer",
                        "description": "子 Agent 最大迭代轮次，默认 30",
                        "default": 30,
                    },
                },
                "required": ["task"],
            },
        },
        {
            "name": "run_subagents_parallel",
            "description": (
                "并行启动多个独立子 Agent，所有子任务同时执行，全部完成后一起返回结果。"
                "适用于资源搜索等需要同时查询多个独立数据源的场景（角色推荐、物件选取、动画校验、场景查找可同时进行）。"
                "tasks 中每项为 {\"task\": str, \"context\": str(可选)}；最多并行 8 个。"
                "⚠️ tasks 必须是原生 array，绝对禁止将 list 序列化为 JSON 字符串后再传入。"
                "禁止在子 Agent 里再次调用并行工具（防止递归）。"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": "子任务列表，每项包含 task（必需）和 context（可选）",
                        "items": {
                            "type": "object",
                            "properties": {
                                "task": {
                                    "type": "string",
                                    "description": "子任务描述，越具体越好",
                                },
                                "context": {
                                    "type": "string",
                                    "description": "传给该子 Agent 的背景信息（可省略）",
                                },
                            },
                            "required": ["task"],
                        },
                    },
                    "max_iterations": {
                        "type": "integer",
                        "description": "每个子 Agent 的最大迭代轮次，默认 30",
                        "default": 30,
                    },
                },
                "required": ["tasks"],
            },
        },
        {
            "name": "pause_and_ask",
            "description": (
                "[子 agent 专用] 遇到 MCP 工具失败、路径找不到、或需要主 Agent 决策时调用。"
                "调用后子 agent 暂停执行，主 Agent 收到 {paused: true, resume_id, question} 的结果。"
                "主 Agent 通过 resume_subagent(resume_id, instruction) 注入指示后，子 agent 从断点继续。"
                "调用后必须立即停止（不得再调用其他任何工具）。"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "向主 Agent 提出的问题（包含：失败工具名、报错信息、可选处理方案）",
                    },
                    "context": {
                        "type": "string",
                        "description": "当前执行进度（已完成哪些步骤、卡在第几步）",
                    },
                },
                "required": ["question"],
            },
        },
        {
            "name": "resume_subagent",
            "description": (
                "恢复一个因 pause_and_ask 暂停的子 Agent，注入主 Agent 指示后从断点继续执行。"
                "resume_id 来自 run_subagent 返回的 paused=true 结果中的 resume_id 字段。"
                "子 Agent 会收到主 Agent 的 instruction 作为 pause_and_ask 的工具结果，然后继续工作。"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "resume_id": {
                        "type": "string",
                        "description": "子 agent pause_and_ask 返回的 resume_id（8位字符串）",
                    },
                    "instruction": {
                        "type": "string",
                        "description": "主 Agent 的指示（明确告知子 agent 如何处理遇到的问题）",
                    },
                },
                "required": ["resume_id", "instruction"],
            },
        },
    ]
