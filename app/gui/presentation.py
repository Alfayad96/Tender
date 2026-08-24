"""Pure presentation helpers for the Streamlit frontend."""

from collections.abc import Iterable
from typing import Any


MISSING_TEXT_VALUES = {
    "",
    "-",
    "—",
    "/",
    "n/a",
    "n.v.",
    "nv",
    "nicht vorhanden",
    "nicht verfügbar",
    "keine angabe",
    "null",
    "undefined",
}


def has_display_value(value: Any) -> bool:
    """Return whether a value contains information worth showing in the UI.

    Numeric zero and ``False`` are intentionally treated as real values.
    """

    if value is None:
        return False

    if isinstance(value, str):
        return value.strip().casefold() not in MISSING_TEXT_VALUES

    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)

    return True


def first_display_value(*values: Any) -> Any:
    """Return the first displayable value, or ``None`` when none exists."""

    return next((value for value in values if has_display_value(value)), None)


def display_items(items: Iterable[Any] | None) -> list[Any]:
    """Remove empty placeholder entries from an optional iterable."""

    if not items:
        return []
    return [item for item in items if has_display_value(item)]
