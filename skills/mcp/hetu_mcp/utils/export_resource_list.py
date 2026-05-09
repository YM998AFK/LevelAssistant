from __future__ import annotations

import argparse
import json
import ssl
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESOURCE_DIR = PACKAGE_ROOT / "resource"
DEFAULT_DEFINITIONS_PATH = PACKAGE_ROOT / "definitions" / "resource_definitions.py"
RESOURCE_SUMMARY_FILENAME = "resouce_summary.json"
RESOURCE_INDEX_FILENAME = "resource_index.json"
UPDATED_RESOURCE_FILENAME = "updated_resource.json"
SPRITE3D_METADATA_FILENAME = "sprite_3d.json"
VFX_METADATA_FILENAME = "vfx.json"
AUDIO_METADATA_FILENAME = "audio.json"
SCENE_METADATA_FILENAME = "scene.json"
SCENE_NAVMESH_DIRNAME = "scene_navmesh"
SPRITE3D_WRITEBACK_FIELDS = [
    "rootRotation",
    "rootScale",
    "animations",
    "center",
    "size",
    "bodyType",
    "direction",
]
VFX_WRITEBACK_FIELDS = ["isLoop", "vfxTime"]
AUDIO_WRITEBACK_FIELDS = ["describe"]
SCENE_WRITEBACK_FIELDS = [
    "scenePath",
    "sceneName",
    "boundsCenter",
    "boundsSize",
    "boundsMin",
    "boundsMax",
    "areaConfig",
    "mapBounds",
    "playerBounds",
    "navMesh",
    "navMeshRect",
]
DEFAULT_URL = (
    "https://tcp-api-sg.testing.hetao101.com/pangu3d-resource-api/v1/list"
    "?language=1&platform=1&levelid=1&view=0&visual=1"
)


CLASS_ID_TO_TYPE = {
    1: "Sprite3D",
    2: "Sprite2D",
    3: "Scene",
    4: "Music",
    5: "Sound",
    6: "VFX",
    7: "Voice",
    8: "Script",
    9: "Video",
    10: "Role",
    11: "UI",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch pangu3d resources and regenerate resource data/definitions."
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="Resource list endpoint.")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_RESOURCE_DIR),
        help="Resource data output directory. Defaults to mcp/hetu_mcp/resource.",
    )
    parser.add_argument(
        "--definitions-output",
        default=str(DEFAULT_DEFINITIONS_PATH),
        help="Generated Python definitions file. Defaults to mcp/hetu_mcp/definitions/resource_definitions.py.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Network timeout in seconds.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Skip TLS certificate verification for test environments.",
    )
    return parser.parse_args()


def coerce_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_attr(value: Any) -> Any:
    if not isinstance(value, str) or not value:
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def type_name_from_class_id(value: Any) -> str:
    class_id = coerce_int(value)
    if class_id is None:
        return "Unknown"
    return CLASS_ID_TO_TYPE.get(class_id, f"Unknown({class_id})")


def build_url(host: str, path_or_url: Any) -> str:
    if not isinstance(path_or_url, str) or not path_or_url:
        return ""
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url
    return urljoin(host.rstrip("/") + "/", path_or_url.lstrip("/"))


def normalize_storages(host: str, storages: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []

    if isinstance(storages, dict):
        items = list(storages.items())
    elif isinstance(storages, list):
        items = []
        for storage in storages:
            if not isinstance(storage, dict):
                continue
            for platform, node in storage.items():
                items.append((platform, node))
    else:
        items = []

    for platform, storage in items:
        if not isinstance(storage, dict):
            continue
        normalized.append(
            {
                "platform": str(platform).replace("all", "common"),
                "url": build_url(host, storage.get("url", "")),
                "raw_url": storage.get("url", ""),
                "url_conf": build_url(host, storage.get("urlConf", "")),
                "raw_url_conf": storage.get("urlConf", ""),
                "md5": storage.get("md5", ""),
                "size": coerce_int(storage.get("size")),
                "has_low": coerce_bool(storage.get("haslow", False)),
                "name": storage.get("name", ""),
            }
        )

    normalized.sort(key=lambda item: (item["platform"] != "windows", item["platform"]))
    return normalized


def pick_primary_storage(storages: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not storages:
        return None
    for preferred in ("windows", "common", "all"):
        for storage in storages:
            if storage["platform"] == preferred:
                return storage
    return storages[0]


def normalize_resource_node(
    *,
    host: str,
    entry_kind: str,
    entry: dict[str, Any],
    resource: dict[str, Any],
    resource_index: int,
) -> dict[str, Any]:
    storages = normalize_storages(host, resource.get("storages"))
    primary_storage = pick_primary_storage(storages) or {}
    entry_class_id = coerce_int(entry.get("classID"))
    resource_class_id = coerce_int(resource.get("classID"))

    return {
        "entry_kind": entry_kind,
        "entry_id": coerce_int(entry.get("iD")),
        "entry_name": entry.get("name", ""),
        "entry_class_id": entry_class_id,
        "entry_type": type_name_from_class_id(entry_class_id),
        "entry_category_id": coerce_int(entry.get("categoryID")),
        "entry_category": entry.get("category", ""),
        "entry_icon": build_url(host, entry.get("icon", "")),
        "entry_release_status": coerce_int(entry.get("releaseStatus")),
        "entry_release_at": coerce_int(entry.get("releaseAt")),
        "entry_created_at": coerce_int(entry.get("createdAt")),
        "entry_updated_at": coerce_int(entry.get("updatedAt")),
        "entry_attr": parse_attr(entry.get("attr")),
        "resource_index": resource_index,
        "resource_id": coerce_int(resource.get("iD")),
        "resource_name": resource.get("name", ""),
        "resource_class_id": resource_class_id,
        "resource_type": type_name_from_class_id(resource_class_id or entry_class_id),
        "resource_icon": build_url(host, resource.get("icon", "")),
        "resource_large_icon": build_url(host, resource.get("largeIcon", "")),
        "resource_preloaded": coerce_bool(resource.get("preloaded", False)),
        "resource_svn_addr": resource.get("svnAddr", ""),
        "resource_ver": coerce_int(resource.get("ver")),
        "storages": storages,
        "platforms": [storage["platform"] for storage in storages],
        "primary_platform": primary_storage.get("platform", ""),
        "primary_url": primary_storage.get("url", ""),
        "primary_raw_url": primary_storage.get("raw_url", ""),
        "primary_url_conf": primary_storage.get("url_conf", ""),
        "primary_raw_url_conf": primary_storage.get("raw_url_conf", ""),
        "primary_md5": primary_storage.get("md5", ""),
        "primary_size": primary_storage.get("size"),
        "primary_has_low": primary_storage.get("has_low", False),
    }


def normalize_sprite_entries(host: str, sprites: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for sprite in sprites:
        if not isinstance(sprite, dict):
            continue
        resources = sprite.get("resources")
        if not isinstance(resources, list):
            resources = []
        normalized.append(
            {
                "entry_kind": "sprite",
                "entry_id": coerce_int(sprite.get("iD")),
                "name": sprite.get("name", ""),
                "class_id": coerce_int(sprite.get("classID")),
                "type": type_name_from_class_id(sprite.get("classID")),
                "category_id": coerce_int(sprite.get("categoryID")),
                "category": sprite.get("category", ""),
                "icon": build_url(host, sprite.get("icon", "")),
                "created_at": coerce_int(sprite.get("createdAt")),
                "updated_at": coerce_int(sprite.get("updatedAt")),
                "release_at": coerce_int(sprite.get("releaseAt")),
                "release_status": coerce_int(sprite.get("releaseStatus")),
                "desc": sprite.get("desc", ""),
                "ver": coerce_int(sprite.get("ver")),
                "resource_count": len(resources),
                "resources": [
                    normalize_resource_node(
                        host=host,
                        entry_kind="sprite",
                        entry=sprite,
                        resource=resource,
                        resource_index=index,
                    )
                    for index, resource in enumerate(resources)
                    if isinstance(resource, dict)
                ],
            }
        )
    return normalized


def normalize_asset_entries(host: str, assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        resource = asset.get("resource")
        resource_records = []
        if isinstance(resource, dict):
            resource_records.append(
                normalize_resource_node(
                    host=host,
                    entry_kind="asset",
                    entry=asset,
                    resource=resource,
                    resource_index=0,
                )
            )
        normalized.append(
            {
                "entry_kind": "asset",
                "entry_id": coerce_int(asset.get("iD")),
                "name": asset.get("name", ""),
                "class_id": coerce_int(asset.get("classID")),
                "type": type_name_from_class_id(asset.get("classID")),
                "category_id": coerce_int(asset.get("categoryID")),
                "category": asset.get("category", ""),
                "icon": build_url(host, asset.get("icon", "")),
                "created_at": coerce_int(asset.get("createdAt")),
                "updated_at": coerce_int(asset.get("updatedAt")),
                "release_status": coerce_int(asset.get("releaseStatus")),
                "ver": coerce_int(asset.get("ver")),
                "attr": parse_attr(asset.get("attr")),
                "resource_count": len(resource_records),
                "resources": resource_records,
            }
        )
    return normalized


def flatten_resources(
    sprite_entries: list[dict[str, Any]], asset_entries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    flat: list[dict[str, Any]] = []
    for entry in sprite_entries:
        flat.extend(entry["resources"])
    for entry in asset_entries:
        flat.extend(entry["resources"])
    flat.sort(
        key=lambda item: (
            item["entry_kind"],
            item["entry_type"],
            item["entry_category"],
            item["entry_name"],
            item["resource_index"],
        )
    )
    return flat


def counter_to_sorted_rows(counter: Counter[str]) -> list[dict[str, Any]]:
    return [
        {"name": name, "count": count}
        for name, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def build_entry_kind_values(flat_resources: list[dict[str, Any]]) -> list[str]:
    return sorted({str(item["entry_kind"]) for item in flat_resources if item.get("entry_kind")})


def build_entry_class_map(flat_resources: list[dict[str, Any]]) -> dict[int, str]:
    class_map: dict[int, str] = {}
    for item in flat_resources:
        class_id = item.get("entry_class_id")
        entry_type = item.get("entry_type")
        if isinstance(class_id, int) and isinstance(entry_type, str) and entry_type:
            class_map.setdefault(class_id, entry_type)
    return dict(sorted(class_map.items()))


def build_entry_category_map(flat_resources: list[dict[str, Any]]) -> dict[int, str]:
    category_votes: dict[int, Counter[str]] = {}
    for item in flat_resources:
        category_id = item.get("entry_category_id")
        category = item.get("entry_category")
        if isinstance(category_id, int) and isinstance(category, str) and category:
            category_votes.setdefault(category_id, Counter())[category] += 1

    category_map: dict[int, str] = {}
    for category_id, votes in sorted(category_votes.items()):
        category_map[category_id] = sorted(votes.items(), key=lambda item: (-item[1], item[0]))[0][0]
    return category_map


def build_brief_resource_records(flat_resources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    brief_records = []
    for item in flat_resources:
        brief_records.append(
            {
                "resource_id": item.get("resource_id"),
                "resource_type": item.get("resource_type", ""),
                "entry_class_id": item.get("entry_class_id"),
                "entry_id": item.get("entry_id"),
                "entry_category_id": item.get("entry_category_id"),
            }
        )
    return brief_records


def load_previous_updated_at(index_path: Path) -> dict[int, int | None]:
    if not index_path.exists():
        return {}

    try:
        records = json.loads(index_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(records, list):
        return {}

    previous: dict[int, int | None] = {}
    for item in records:
        if not isinstance(item, dict):
            continue
        resource_id = coerce_int(item.get("resource_id"))
        if resource_id is None:
            continue
        previous[resource_id] = coerce_int(item.get("entry_updated_at"))
    return previous


def build_updated_resources(
    flat_resources: list[dict[str, Any]],
    previous_updated_at: dict[int, int | None],
) -> list[int]:
    updated_resource_ids: list[int] = []
    for item in flat_resources:
        resource_id = coerce_int(item.get("resource_id"))
        if resource_id is None:
            continue

        current_updated_at = coerce_int(item.get("entry_updated_at"))
        if resource_id not in previous_updated_at:
            updated_resource_ids.append(resource_id)
            continue
        if previous_updated_at[resource_id] != current_updated_at:
            updated_resource_ids.append(resource_id)

    return sorted(set(updated_resource_ids))


def extract_updated_resource_ids(payload: Any) -> list[int]:
    if isinstance(payload, dict):
        values = payload.get("updated_resource")
    else:
        values = payload

    if not isinstance(values, list):
        return []

    resource_ids: list[int] = []
    for value in values:
        resource_id = coerce_int(value)
        if resource_id is not None:
            resource_ids.append(resource_id)
    return sorted(set(resource_ids))


def load_existing_updated_resources(*paths: Path) -> list[int]:
    resource_ids: set[int] = set()
    for path in paths:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        resource_ids.update(extract_updated_resource_ids(payload))
    return sorted(resource_ids)


def build_updated_resource_payload(
    current_updated_resources: list[int],
    existing_updated_resources: list[int],
) -> dict[str, list[int]]:
    merged = sorted(set(existing_updated_resources).union(current_updated_resources))
    return {"updated_resource": merged}


def build_resource_summary(
    *,
    source_url: str,
    host: str,
    summary: dict[str, Any],
    flat_resources: list[dict[str, Any]],
) -> dict[str, Any]:
    entry_kind_values = build_entry_kind_values(flat_resources)
    entry_class_map = build_entry_class_map(flat_resources)
    entry_category_map = build_entry_category_map(flat_resources)

    return {
        "generated_at_utc": summary["generated_at_utc"],
        "source_url": source_url,
        "host": host,
        "entry_kind_values": entry_kind_values,
        "entry_class_id_to_type": {str(key): value for key, value in entry_class_map.items()},
        "entry_category_id_to_category": {
            str(key): value for key, value in entry_category_map.items()
        },
        "entry_counts": summary["entry_counts"],
        "resource_counts": summary["resource_counts"],
        "by_entry_type": summary["by_entry_type"],
        "by_resource_type": summary["by_resource_type"],
        "by_category": summary["by_category"],
        "by_platform": summary["by_platform"],
        "resources": build_brief_resource_records(flat_resources),
    }


def build_summary(
    *,
    source_url: str,
    host: str,
    sprite_entries: list[dict[str, Any]],
    asset_entries: list[dict[str, Any]],
    flat_resources: list[dict[str, Any]],
) -> dict[str, Any]:
    entry_types = Counter(entry["type"] for entry in sprite_entries + asset_entries if entry["type"])
    resource_types = Counter(item["resource_type"] for item in flat_resources if item["resource_type"])
    entry_categories = Counter(
        entry["category"] for entry in sprite_entries + asset_entries if entry["category"]
    )
    resource_platforms = Counter(
        platform for item in flat_resources for platform in item.get("platforms", []) if platform
    )

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": source_url,
        "host": host,
        "entry_counts": {
            "sprites": len(sprite_entries),
            "assets": len(asset_entries),
            "total_entries": len(sprite_entries) + len(asset_entries),
        },
        "resource_counts": {
            "sprite_resources": sum(entry["resource_count"] for entry in sprite_entries),
            "asset_resources": sum(entry["resource_count"] for entry in asset_entries),
            "total_resources": len(flat_resources),
        },
        "by_entry_type": counter_to_sorted_rows(entry_types),
        "by_resource_type": counter_to_sorted_rows(resource_types),
        "by_category": counter_to_sorted_rows(entry_categories),
        "by_platform": counter_to_sorted_rows(resource_platforms),
    }


def render_readme(summary: dict[str, Any]) -> str:
    lines = [
        "# Resource Export",
        "",
        f"- generated_at_utc: `{summary['generated_at_utc']}`",
        f"- source_url: `{summary['source_url']}`",
        f"- host: `{summary['host']}`",
        f"- total_entries: `{summary['entry_counts']['total_entries']}`",
        f"- total_resources: `{summary['resource_counts']['total_resources']}`",
        "",
        "## Files",
        "",
        f"- `{RESOURCE_SUMMARY_FILENAME}`: compact resource data for quick checks",
        f"- `{UPDATED_RESOURCE_FILENAME}`: pending resource ids changed since previous exports",
        f"- `{RESOURCE_INDEX_FILENAME}`: complete flattened resource records",
        f"- `{AUDIO_METADATA_FILENAME}`: extracted Music/Sound semantic descriptions",
        f"- `{SPRITE3D_METADATA_FILENAME}`: extracted Sprite3D/Role transform and MeshPartSettings metadata",
        f"- `{VFX_METADATA_FILENAME}`: extracted VFX duration and loop metadata",
        f"- `{SCENE_METADATA_FILENAME}`: extracted Scene bounds and lightweight NavMesh references",
        f"- `{SCENE_NAVMESH_DIRNAME}/`: full Scene NavMesh payloads keyed by resource_id, including precomputed graph data",
        "- `../definitions/resource_definitions.py`: generated lookup and validation helpers",
        "",
        "## Top Resource Types",
        "",
    ]

    for row in summary["by_resource_type"][:10]:
        lines.append(f"- `{row['name']}`: {row['count']}")

    lines.extend(
        [
            "",
            "## Top Categories",
            "",
        ]
    )

    for row in summary["by_category"][:10]:
        lines.append(f"- `{row['name']}`: {row['count']}")

    lines.append("")
    return "\n".join(lines)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def scalar_to_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def dumps_compact_vectors(value: Any, level: int = 0) -> str:
    indent = "  " * level
    child_indent = "  " * (level + 1)
    if isinstance(value, dict):
        if not value:
            return "{}"
        parts = [
            f"{child_indent}{scalar_to_json(key)}: {dumps_compact_vectors(item, level + 1)}"
            for key, item in value.items()
        ]
        return "{\n" + ",\n".join(parts) + "\n" + indent + "}"
    if isinstance(value, list):
        if not value:
            return "[]"
        if all(is_number(item) for item in value):
            return "[" + ",".join(scalar_to_json(item) for item in value) + "]"
        parts = [f"{child_indent}{dumps_compact_vectors(item, level + 1)}" for item in value]
        return "[\n" + ",\n".join(parts) + "\n" + indent + "]"
    return scalar_to_json(value)


def load_metadata_by_resource_id(path: Path) -> dict[int, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        rows = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(rows, list):
        return {}

    metadata: dict[int, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        resource_id = coerce_int(row.get("resource_id"))
        if resource_id is None:
            continue
        metadata[resource_id] = row
    return metadata


def apply_parsed_metadata(
    records: list[dict[str, Any]],
    resource_dir: Path,
) -> tuple[int, int, int, int]:
    sprite_metadata = load_metadata_by_resource_id(resource_dir / SPRITE3D_METADATA_FILENAME)
    vfx_metadata = load_metadata_by_resource_id(resource_dir / VFX_METADATA_FILENAME)
    audio_metadata = load_metadata_by_resource_id(resource_dir / AUDIO_METADATA_FILENAME)
    scene_metadata = load_metadata_by_resource_id(resource_dir / SCENE_METADATA_FILENAME)

    sprite_updated = 0
    vfx_updated = 0
    audio_updated = 0
    scene_updated = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        resource_id = coerce_int(record.get("resource_id"))
        if resource_id is None:
            continue

        sprite_row = sprite_metadata.get(resource_id)
        if sprite_row is not None:
            for field in SPRITE3D_WRITEBACK_FIELDS:
                record[field] = sprite_row.get(field)
            sprite_updated += 1

        vfx_row = vfx_metadata.get(resource_id)
        if vfx_row is not None:
            for field in VFX_WRITEBACK_FIELDS:
                record[field] = vfx_row.get(field)
            vfx_updated += 1

        audio_row = audio_metadata.get(resource_id)
        if audio_row is not None:
            for field in AUDIO_WRITEBACK_FIELDS:
                record[field] = audio_row.get(field)
            audio_updated += 1

        scene_row = scene_metadata.get(resource_id)
        if scene_row is not None:
            for field in SCENE_WRITEBACK_FIELDS:
                record[field] = scene_row.get(field)
            scene_updated += 1

    return sprite_updated, vfx_updated, audio_updated, scene_updated


def enum_member_name(value: str) -> str:
    name = "".join(ch if ch.isalnum() else "_" for ch in value.upper()).strip("_")
    return name or "UNKNOWN"


def render_python_literal(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=4)


def render_resource_definitions(
    *,
    entry_kind_values: list[str],
    entry_class_map: dict[int, str],
    entry_category_map: dict[int, str],
) -> str:
    enum_lines = [
        f"    {enum_member_name(value)} = {value!r}" for value in entry_kind_values
    ]
    if not enum_lines:
        enum_lines = ["    UNKNOWN = 'unknown'"]

    entry_kind_literal = render_python_literal(entry_kind_values)
    class_map_literal = render_python_literal(entry_class_map)
    category_map_literal = render_python_literal(entry_category_map)

    return f'''"""
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
RESOURCE_SUMMARY_PATH = RESOURCE_DIR / "{RESOURCE_SUMMARY_FILENAME}"
RESOURCE_INDEX_PATH = RESOURCE_DIR / "{RESOURCE_INDEX_FILENAME}"
UPDATED_RESOURCE_PATH = RESOURCE_DIR / "{UPDATED_RESOURCE_FILENAME}"


class EntryKind(str, Enum):
{chr(10).join(enum_lines)}


ENTRY_KIND_VALUES: tuple[str, ...] = tuple({entry_kind_literal})
ENTRY_CLASS_ID_TO_TYPE: dict[int, str] = {{
    int(key): value for key, value in {class_map_literal}.items()
}}
ENTRY_CATEGORY_ID_TO_CATEGORY: dict[int, str] = {{
    int(key): value for key, value in {category_map_literal}.items()
}}


def resource_data_exists() -> bool:
    return (
        RESOURCE_SUMMARY_PATH.exists()
        and RESOURCE_INDEX_PATH.exists()
        and UPDATED_RESOURCE_PATH.exists()
    )


def ensure_resource_data() -> None:
    if resource_data_exists():
        return

    script_path = Path(__file__).resolve().parents[1] / "utils" / "export_resource_list.py"
    if not script_path.exists():
        raise FileNotFoundError(f"Resource export script not found: {{script_path}}")

    subprocess.run(
        [sys.executable, str(script_path), "--insecure"],
        check=True,
        cwd=str(Path(__file__).resolve().parents[1]),
    )
    load_resource_summary.cache_clear()
    load_resource_index.cache_clear()
    load_updated_resources.cache_clear()


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
        raise ValueError(f"Resource index must be a list: {{RESOURCE_INDEX_PATH}}")
    return payload


@lru_cache(maxsize=1)
def load_updated_resources() -> list[int]:
    ensure_resource_data()
    if not UPDATED_RESOURCE_PATH.exists():
        return []
    payload = json.loads(UPDATED_RESOURCE_PATH.read_text(encoding="utf-8"))
    values = payload.get("updated_resource") if isinstance(payload, dict) else payload
    if not isinstance(values, list):
        raise ValueError(
            f"Updated resources must be a list or an object with updated_resource: {{UPDATED_RESOURCE_PATH}}"
        )

    resource_ids: list[int] = []
    for value in values:
        resource_id = _coerce_int(value)
        if resource_id is not None:
            resource_ids.append(resource_id)
    return sorted(set(resource_ids))


def iter_resource_summaries() -> list[dict[str, Any]]:
    resources = load_resource_summary().get("resources", [])
    if not isinstance(resources, list):
        raise ValueError(f"Resource summary resources must be a list: {{RESOURCE_SUMMARY_PATH}}")
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


def is_updated_resource(resource_id: int | str) -> bool:
    target_id = _coerce_int(resource_id)
    return target_id is not None and target_id in set(load_updated_resources())


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
        return {{
            "valid": False,
            "reason": f"Unknown entry_kind: {{target_entry_kind}}",
            "count": 0,
        }}

    target_entry_class_id = _coerce_int(entry_class_id)
    if target_entry_class_id is not None:
        expected_type = ENTRY_CLASS_ID_TO_TYPE.get(target_entry_class_id)
        if expected_type is None:
            return {{
                "valid": False,
                "reason": f"Unknown entry_class_id: {{target_entry_class_id}}",
                "count": 0,
            }}
        if entry_type is not None and entry_type != expected_type:
            return {{
                "valid": False,
                "reason": (
                    f"entry_class_id {{target_entry_class_id}} maps to "
                    f"{{expected_type}}, not {{entry_type}}"
                ),
                "count": 0,
            }}

    target_entry_category_id = _coerce_int(entry_category_id)
    if target_entry_category_id is not None:
        expected_category = ENTRY_CATEGORY_ID_TO_CATEGORY.get(target_entry_category_id)
        if expected_category is None:
            return {{
                "valid": False,
                "reason": f"Unknown entry_category_id: {{target_entry_category_id}}",
                "count": 0,
            }}
        if entry_category is not None and entry_category != expected_category:
            return {{
                "valid": False,
                "reason": (
                    f"entry_category_id {{target_entry_category_id}} maps to "
                    f"{{expected_category}}, not {{entry_category}}"
                ),
                "count": 0,
            }}

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
        return {{"valid": False, "reason": "No matching resource", "count": 0}}

    if require_primary_url:
        missing_url = [item for item in matches if not item.get("primary_url")]
        if missing_url:
            return {{
                "valid": False,
                "reason": "Matching resource exists but primary_url is missing",
                "count": len(matches),
                "resource": missing_url[0],
            }}

    return {{
        "valid": True,
        "reason": "",
        "count": len(matches),
        "resource": matches[0] if len(matches) == 1 else None,
    }}


def is_valid_resource(**kwargs: Any) -> bool:
    return bool(validate_resource(**kwargs).get("valid"))
'''


def write_resource_definitions(
    path: Path,
    *,
    entry_kind_values: list[str],
    entry_class_map: dict[int, str],
    entry_category_map: dict[int, str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_resource_definitions(
            entry_kind_values=entry_kind_values,
            entry_class_map=entry_class_map,
            entry_category_map=entry_category_map,
        ),
        encoding="utf-8",
    )


def fetch_payload(url: str, timeout: int, insecure: bool) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "HetuAIGC/export_resource_list.py",
        },
    )
    context = ssl._create_unverified_context() if insecure else ssl.create_default_context()

    try:
        with urlopen(request, timeout=timeout, context=context) as response:
            data = response.read().decode("utf-8")
    except HTTPError as exc:
        raise RuntimeError(f"HTTP error {exc.code}: {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"Failed to fetch resource list: {exc}") from exc

    try:
        payload = json.loads(data)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Response is not valid JSON") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("Top-level response is not an object")
    return payload


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    definitions_path = Path(args.definitions_output)
    resource_index_path = output_dir / RESOURCE_INDEX_FILENAME
    previous_updated_at = load_previous_updated_at(resource_index_path)

    try:
        payload = fetch_payload(args.url, args.timeout, args.insecure)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        if not args.insecure:
            print("Tip: rerun with --insecure in test environments.", file=sys.stderr)
        return 1

    code = coerce_int(payload.get("code"))
    if code != 200:
        print(
            f"Unexpected API response code: {payload.get('code')}, msg={payload.get('msg')}",
            file=sys.stderr,
        )
        return 1

    data = payload.get("data")
    if not isinstance(data, dict):
        print("Response data field is missing or invalid.", file=sys.stderr)
        return 1

    host = str(data.get("host", "") or "")
    sprites = data.get("sprites")
    assets = data.get("assets")

    if not isinstance(sprites, list):
        sprites = []
    if not isinstance(assets, list):
        assets = []

    sprite_entries = normalize_sprite_entries(host, sprites)
    asset_entries = normalize_asset_entries(host, assets)
    flat_resources = flatten_resources(sprite_entries, asset_entries)
    summary = build_summary(
        source_url=args.url,
        host=host,
        sprite_entries=sprite_entries,
        asset_entries=asset_entries,
        flat_resources=flat_resources,
    )
    resource_summary = build_resource_summary(
        source_url=args.url,
        host=host,
        summary=summary,
        flat_resources=flat_resources,
    )
    current_updated_resources = build_updated_resources(flat_resources, previous_updated_at)
    updated_resource_path = output_dir / UPDATED_RESOURCE_FILENAME
    updated_resource_payload = build_updated_resource_payload(
        current_updated_resources,
        load_existing_updated_resources(updated_resource_path, output_dir / RESOURCE_SUMMARY_FILENAME),
    )
    entry_kind_values = build_entry_kind_values(flat_resources)
    entry_class_map = build_entry_class_map(flat_resources)
    entry_category_map = build_entry_category_map(flat_resources)

    sprite_writeback_count, vfx_writeback_count, audio_writeback_count, scene_writeback_count = apply_parsed_metadata(
        flat_resources,
        output_dir,
    )
    write_json(output_dir / RESOURCE_SUMMARY_FILENAME, resource_summary)
    write_json(updated_resource_path, updated_resource_payload)
    resource_index_path.write_text(
        dumps_compact_vectors(flat_resources) + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(render_readme(summary), encoding="utf-8")
    write_resource_definitions(
        definitions_path,
        entry_kind_values=entry_kind_values,
        entry_class_map=entry_class_map,
        entry_category_map=entry_category_map,
    )

    print(f"Exported resource data to: {output_dir}")
    print(f"Generated definitions: {definitions_path}")
    print(f"Entries: {summary['entry_counts']['total_entries']}")
    print(f"Resources: {summary['resource_counts']['total_resources']}")
    print(
        "Updated resources: "
        f"current={len(current_updated_resources)}, "
        f"merged={len(updated_resource_payload['updated_resource'])}"
    )
    print(
        "Parsed metadata writeback: "
        f"Sprite3D/Role={sprite_writeback_count}, "
        f"VFX={vfx_writeback_count}, "
        f"Audio={audio_writeback_count}, "
        f"Scene={scene_writeback_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
