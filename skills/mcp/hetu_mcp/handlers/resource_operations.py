"""
Resource lookup and validation operations.
"""

from __future__ import annotations

from typing import Any, Dict, List

from definitions.resource_definitions import (
    ensure_resource_data,
    find_resources as find_resource_records,
    get_resource as get_resource_record,
    validate_resource as validate_resource_record,
)


def get_resource(resource_id: int | str) -> Dict[str, Any]:
    ensure_resource_data()
    resource = get_resource_record(resource_id)
    if resource is None:
        raise ValueError(f"Resource not found: {resource_id}")
    return resource


def find_resources(
    resource_id: int | str | None = None,
    resource_name: str | None = None,
    resource_type: str | None = None,
    entry_id: int | str | None = None,
    entry_name: str | None = None,
    entry_kind: str | None = None,
    entry_class_id: int | str | None = None,
    entry_type: str | None = None,
    entry_category_id: int | str | None = None,
    entry_category: str | None = None,
    limit: int | None = 20,
) -> Dict[str, Any]:
    ensure_resource_data()
    if limit is not None and limit <= 0:
        raise ValueError("limit must be greater than 0")

    resources: List[Dict[str, Any]] = find_resource_records(
        resource_id=resource_id,
        resource_name=resource_name,
        resource_type=resource_type,
        entry_id=entry_id,
        entry_name=entry_name,
        entry_kind=entry_kind,
        entry_class_id=entry_class_id,
        entry_type=entry_type,
        entry_category_id=entry_category_id,
        entry_category=entry_category,
        limit=limit,
    )
    return {
        "count": len(resources),
        "limit": limit,
        "resources": resources,
    }


def validate_resource(
    resource_id: int | str | None = None,
    resource_name: str | None = None,
    resource_type: str | None = None,
    entry_kind: str | None = None,
    entry_class_id: int | str | None = None,
    entry_type: str | None = None,
    entry_category_id: int | str | None = None,
    entry_category: str | None = None,
    require_primary_url: bool = False,
) -> Dict[str, Any]:
    ensure_resource_data()
    return validate_resource_record(
        resource_id=resource_id,
        resource_name=resource_name,
        resource_type=resource_type,
        entry_kind=entry_kind,
        entry_class_id=entry_class_id,
        entry_type=entry_type,
        entry_category_id=entry_category_id,
        entry_category=entry_category,
        require_primary_url=require_primary_url,
    )
