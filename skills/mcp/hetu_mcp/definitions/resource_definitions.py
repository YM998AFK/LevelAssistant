"""
Generated resource lookup helpers.

Do not edit manually. Regenerate with:
python mcp/hetu_mcp/utils/export_resource_list.py --insecure
"""

from __future__ import annotations

import json
import subprocess
import sys
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any


RESOURCE_DIR = Path(__file__).resolve().parents[1] / "resource"
RESOURCE_SUMMARY_PATH = RESOURCE_DIR / "resouce_summary.json"
RESOURCE_INDEX_PATH = RESOURCE_DIR / "resource_index.json"


class EntryKind(str, Enum):
    ASSET = 'asset'
    SPRITE = 'sprite'


ENTRY_KIND_VALUES: tuple[str, ...] = tuple([
    "asset",
    "sprite"
])
ENTRY_CLASS_ID_TO_TYPE: dict[int, str] = {
    int(key): value for key, value in {
    "1": "Sprite3D",
    "2": "Sprite2D",
    "3": "Scene",
    "4": "Music",
    "5": "Sound",
    "6": "VFX",
    "8": "Script",
    "9": "Video",
    "10": "Role",
    "11": "UI"
}.items()
}
ENTRY_CATEGORY_ID_TO_CATEGORY: dict[int, str] = {
    int(key): value for key, value in {
    "1": "test",
    "11": "test",
    "12": "1231",
    "13": "Courses",
    "14": "Courses（作废）",
    "15": "样课（作废）",
    "16": "样课",
    "18": "样课2.0",
    "19": "样课2.0",
    "21": "活动课",
    "24": "DEMO",
    "25": "Demo",
    "27": "TEST",
    "28": "C++Python 1-2",
    "29": "C++Python 1-1",
    "30": "C++Python 1-1",
    "32": "C++Python 1-2",
    "33": "C++Py",
    "39": "BGMc++py",
    "40": "QWCL1/1",
    "41": "QWCL1/2",
    "42": "QWCL1/3",
    "44": "QWCL1/4",
    "45": "QWCL2/3",
    "46": "QWCL2/1",
    "47": "QWCL2/2",
    "49": "QWCL4/2",
    "53": "QWCL3/4",
    "60": "QWCL3/2",
    "61": "QWCL3/1",
    "62": "QWCL3/3",
    "63": "实验1.5QWCL1/3",
    "64": "实验1.2QWCL1/3",
    "65": "QWCL3/3倍速1.5",
    "67": "QWCL4/1",
    "69": "QWCL4/3",
    "70": "QWCL4/4",
    "72": "QWCL5/1",
    "73": "QWCL5/3",
    "75": "QWCL5/4",
    "76": "QWCL6/1",
    "77": "QWCL6/2",
    "78": "QWCL6/3",
    "79": "加速迭代L1-2",
    "80": "加速迭代L1-1",
    "81": "加速迭代L1-3",
    "82": "加速迭代L1-4",
    "84": "QWCL5/2",
    "85": "QWCL6/4",
    "86": "加速迭代L2-1",
    "88": "加速迭代L2-3",
    "91": "加速迭代L2-2",
    "92": "加速迭代L2-4",
    "93": "QWCL1-4全向车",
    "94": "QWCL2-3全向车",
    "95": "加速迭代L3-3",
    "96": "加速迭代L3-4",
    "97": "加速迭代L3-2",
    "98": "加速迭代L3-1",
    "101": "C++L7",
    "102": "C++ L7-12",
    "103": "QWCL7/1",
    "104": "QWCL7/3",
    "105": "QWCL7/4",
    "106": "QWCL7/2",
    "107": "C++L8",
    "108": "C++L9",
    "109": "C++L10",
    "110": "C++L11",
    "111": "C++L12",
    "112": "QWCL8/2",
    "113": "QWCL8/1",
    "114": "QWCL8/3",
    "115": "QWCL8/3（新版）",
    "116": "QWCL8/1新",
    "117": "QWCL8/1新2",
    "118": "QWCL9/2",
    "119": "QWCL9/1",
    "120": "QWCL8/4",
    "121": "QWCL8/4",
    "122": "QWCL9/3",
    "123": "QWCL4-4全向车",
    "124": "QWCL9/4",
    "125": "QWC迭代L5-4",
    "127": "QWCL10/2",
    "128": "QWCL10/1",
    "129": "QWCL8/1迭代",
    "130": "QWCL8/2迭代",
    "131": "QWCL10/3",
    "132": "QWCL10/4",
    "133": "QWCL11/3",
    "134": "QWCL11/1",
    "136": "QWCL迭8/4",
    "137": "QWCL11/2",
    "138": "QWCL10-4迭代",
    "139": "QWCL12/2",
    "140": "QWCL12/3",
    "141": "QWCL12/1",
    "142": "QWCL11/4",
    "143": "ui1",
    "144": "QWCL12/4上半节",
    "145": "QWCL12/4下",
    "146": "QWCL7/4迭代",
    "148": "趣C",
    "149": "QWCL8/3全向车迭代",
    "150": "C++ L13-18",
    "151": "C++L13",
    "152": "C++L14",
    "153": "C++L15",
    "154": "C++L16",
    "157": "QWCL13/2废弃",
    "158": "QWCL13/1废弃",
    "159": "QWCL13/2低年级",
    "160": "QWCL13/2高年级",
    "161": "QWCL13/1低年级",
    "162": "QWCL13/1高年级",
    "163": "关卡场景",
    "165": "QWCL13/3低年级",
    "166": "QWCDL14/1",
    "167": "关卡通用音效",
    "168": "关卡通用BGM",
    "169": "QWCDL13/4",
    "170": "QWCGL13/4",
    "171": "QWCL15/3低年级",
    "172": "QWCL14/2低年级",
    "173": "QWCGL14/1高年级",
    "174": "QWCGL14/1高",
    "175": "QWCL13/3高年级",
    "176": "QWCL15/1低",
    "177": "QWCL14/3高年级",
    "178": "QWCL14/3低年级",
    "179": "QWCL14/2高年级",
    "180": "QWCL15-4低",
    "182": "QWCL10-4 全向车迭代",
    "183": "QWCL14-4高",
    "184": "QWCL14-4 低",
    "185": "关卡demo"
}.items()
}


def resource_data_exists() -> bool:
    return RESOURCE_SUMMARY_PATH.exists() and RESOURCE_INDEX_PATH.exists()


def ensure_resource_data() -> None:
    if resource_data_exists():
        return

    script_path = Path(__file__).resolve().parents[1] / "utils" / "export_resource_list.py"
    if not script_path.exists():
        raise FileNotFoundError(f"Resource export script not found: {script_path}")

    subprocess.run(
        [sys.executable, str(script_path), "--insecure"],
        check=True,
        cwd=str(Path(__file__).resolve().parents[1]),
    )
    load_resource_summary.cache_clear()
    load_resource_index.cache_clear()


def _coerce_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@lru_cache(maxsize=1)
def load_resource_summary() -> dict[str, Any]:
    ensure_resource_data()
    return json.loads(RESOURCE_SUMMARY_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_resource_index() -> list[dict[str, Any]]:
    ensure_resource_data()
    payload = json.loads(RESOURCE_INDEX_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Resource index must be a list: {RESOURCE_INDEX_PATH}")
    return payload


def iter_resource_summaries() -> list[dict[str, Any]]:
    resources = load_resource_summary().get("resources", [])
    if not isinstance(resources, list):
        raise ValueError(f"Resource summary resources must be a list: {RESOURCE_SUMMARY_PATH}")
    return resources


def iter_resources() -> list[dict[str, Any]]:
    return load_resource_index()


def get_resource_summary(resource_id: int | str, default: Any = None) -> dict[str, Any] | Any:
    target_id = _coerce_int(resource_id)
    if target_id is None:
        return default
    for resource in iter_resource_summaries():
        if resource.get("resource_id") == target_id:
            return resource
    return default


def get_resource(resource_id: int | str, default: Any = None) -> dict[str, Any] | Any:
    target_id = _coerce_int(resource_id)
    if target_id is None:
        return default
    for resource in load_resource_index():
        if resource.get("resource_id") == target_id:
            return resource
    return default


def is_valid_resource_id(resource_id: int | str) -> bool:
    return get_resource_summary(resource_id) is not None


def find_resources(
    *,
    resource_id: int | str | None = None,
    resource_name: str | None = None,
    resource_type: str | None = None,
    entry_id: int | str | None = None,
    entry_name: str | None = None,
    entry_kind: str | EntryKind | None = None,
    entry_class_id: int | str | None = None,
    entry_type: str | None = None,
    entry_category_id: int | str | None = None,
    entry_category: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    target_resource_id = _coerce_int(resource_id)
    target_entry_id = _coerce_int(entry_id)
    target_entry_class_id = _coerce_int(entry_class_id)
    target_entry_category_id = _coerce_int(entry_category_id)
    target_entry_kind = entry_kind.value if isinstance(entry_kind, EntryKind) else entry_kind

    matches: list[dict[str, Any]] = []
    for resource in load_resource_index():
        if target_resource_id is not None and resource.get("resource_id") != target_resource_id:
            continue
        if resource_name is not None and resource.get("resource_name") != resource_name:
            continue
        if resource_type is not None and resource.get("resource_type") != resource_type:
            continue
        if target_entry_id is not None and resource.get("entry_id") != target_entry_id:
            continue
        if entry_name is not None and resource.get("entry_name") != entry_name:
            continue
        if target_entry_kind is not None and resource.get("entry_kind") != target_entry_kind:
            continue
        if (
            target_entry_class_id is not None
            and resource.get("entry_class_id") != target_entry_class_id
        ):
            continue
        if entry_type is not None and resource.get("entry_type") != entry_type:
            continue
        if (
            target_entry_category_id is not None
            and resource.get("entry_category_id") != target_entry_category_id
        ):
            continue
        if entry_category is not None and resource.get("entry_category") != entry_category:
            continue

        matches.append(resource)
        if limit is not None and len(matches) >= limit:
            break

    return matches


def validate_resource(
    *,
    resource_id: int | str | None = None,
    resource_name: str | None = None,
    resource_type: str | None = None,
    entry_kind: str | EntryKind | None = None,
    entry_class_id: int | str | None = None,
    entry_type: str | None = None,
    entry_category_id: int | str | None = None,
    entry_category: str | None = None,
    require_primary_url: bool = False,
) -> dict[str, Any]:
    target_entry_kind = entry_kind.value if isinstance(entry_kind, EntryKind) else entry_kind
    if target_entry_kind is not None and target_entry_kind not in ENTRY_KIND_VALUES:
        return {
            "valid": False,
            "reason": f"Unknown entry_kind: {target_entry_kind}",
            "count": 0,
        }

    target_entry_class_id = _coerce_int(entry_class_id)
    if target_entry_class_id is not None:
        expected_type = ENTRY_CLASS_ID_TO_TYPE.get(target_entry_class_id)
        if expected_type is None:
            return {
                "valid": False,
                "reason": f"Unknown entry_class_id: {target_entry_class_id}",
                "count": 0,
            }
        if entry_type is not None and entry_type != expected_type:
            return {
                "valid": False,
                "reason": (
                    f"entry_class_id {target_entry_class_id} maps to "
                    f"{expected_type}, not {entry_type}"
                ),
                "count": 0,
            }

    target_entry_category_id = _coerce_int(entry_category_id)
    if target_entry_category_id is not None:
        expected_category = ENTRY_CATEGORY_ID_TO_CATEGORY.get(target_entry_category_id)
        if expected_category is None:
            return {
                "valid": False,
                "reason": f"Unknown entry_category_id: {target_entry_category_id}",
                "count": 0,
            }
        if entry_category is not None and entry_category != expected_category:
            return {
                "valid": False,
                "reason": (
                    f"entry_category_id {target_entry_category_id} maps to "
                    f"{expected_category}, not {entry_category}"
                ),
                "count": 0,
            }

    matches = find_resources(
        resource_id=resource_id,
        resource_name=resource_name,
        resource_type=resource_type,
        entry_kind=target_entry_kind,
        entry_class_id=target_entry_class_id,
        entry_type=entry_type,
        entry_category_id=target_entry_category_id,
        entry_category=entry_category,
    )
    if not matches:
        return {"valid": False, "reason": "No matching resource", "count": 0}

    if require_primary_url:
        missing_url = [item for item in matches if not item.get("primary_url")]
        if missing_url:
            return {
                "valid": False,
                "reason": "Matching resource exists but primary_url is missing",
                "count": len(matches),
                "resource": missing_url[0],
            }

    return {
        "valid": True,
        "reason": "",
        "count": len(matches),
        "resource": matches[0] if len(matches) == 1 else None,
    }


def is_valid_resource(**kwargs: Any) -> bool:
    return bool(validate_resource(**kwargs).get("valid"))
