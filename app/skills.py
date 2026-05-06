"""Skill 包加载：递归扫描 skills/ 下所有 SKILL.md，支持任意嵌套结构"""
from __future__ import annotations

import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from .config import cursor_skills_dir


@dataclass
class Skill:
    id: str
    path: Path
    name: str
    description: str
    content: str
    mode: Optional[str] = None


def _parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {"_body": text}
    fm_block, body = m.group(1), m.group(2)
    fm = {"_body": body}
    for line in fm_block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def load_skills() -> List[Skill]:
    """扫描 skills/.cursor/skills 下所有 SKILL.md"""
    root = cursor_skills_dir()
    if not root.exists():
        return []
    skills: List[Skill] = []
    for skill_md in root.rglob("SKILL.md"):
        if not skill_md.is_file():
            continue
        try:
            text = skill_md.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = _parse_frontmatter(text)
        folder = skill_md.parent
        try:
            rel = folder.relative_to(root)
            skill_id = str(rel).replace(os.sep, "/") if str(rel) != "." else folder.name
        except ValueError:
            skill_id = folder.name
        skills.append(Skill(
            id=skill_id,
            path=folder,
            name=fm.get("name", folder.name),
            description=fm.get("description", ""),
            content=fm.get("_body", "").strip(),
            mode=fm.get("mode"),
        ))
    skills.sort(key=lambda s: s.id)
    return skills


def skills_for_mode(mode: str) -> List[Skill]:
    all_skills = load_skills()
    exact = [s for s in all_skills if s.mode == mode]
    generic = [s for s in all_skills if s.mode is None]
    return exact + generic
