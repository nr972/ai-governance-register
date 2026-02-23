from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from api.models import AuditLog


def _serialize_value(value: Any) -> Any:
    """Convert a value to a JSON-serializable form."""
    if value is None:
        return None
    if hasattr(value, "value"):  # Enum
        return value.value
    if isinstance(value, (datetime,)):
        return value.isoformat()
    if hasattr(value, "isoformat"):  # date
        return value.isoformat()
    return value


def compute_diff(
    old_data: Optional[dict], new_data: dict
) -> dict[str, dict[str, Any]]:
    """Compute field-level diff between old and new data.

    Returns dict of ``{field: {"old": old_val, "new": new_val}}`` for
    changed fields only.  If *old_data* is ``None`` (creation), every
    field in *new_data* is included with ``old=None``.
    """
    changes: dict[str, dict[str, Any]] = {}
    if old_data is None:
        for key, value in new_data.items():
            changes[key] = {"old": None, "new": _serialize_value(value)}
        return changes

    for key, new_value in new_data.items():
        old_value = old_data.get(key)
        serialized_old = _serialize_value(old_value)
        serialized_new = _serialize_value(new_value)
        if serialized_old != serialized_new:
            changes[key] = {"old": serialized_old, "new": serialized_new}
    return changes


def record_change(
    db: Session,
    *,
    system_id: str,
    entity_type: str,
    entity_id: str,
    action: str,
    old_data: Optional[dict] = None,
    new_data: Optional[dict] = None,
) -> AuditLog:
    """Write an audit-log entry for a create/update/delete action.

    * On **create**: pass ``old_data=None``, ``new_data={...}``.
    * On **update**: pass both ``old_data`` and ``new_data``.
    * On **delete**: pass ``old_data={...}``, ``new_data=None``.
    """
    if action == "created":
        changes = compute_diff(None, new_data or {})
    elif action == "updated":
        changes = compute_diff(old_data or {}, new_data or {})
    elif action == "deleted":
        changes = {
            k: {"old": _serialize_value(v), "new": None}
            for k, v in (old_data or {}).items()
        }
    else:
        changes = {}

    entry = AuditLog(
        system_id=system_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        changes=changes,
    )
    db.add(entry)
    return entry
