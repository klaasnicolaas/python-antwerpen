"""Asynchronous Python client providing Open Data information of Antwerpen."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class DisabledParking:
    """Object representing a disabled parking."""

    entry_id: int
    number: int
    color: str | None
    address: str
    gis_id: str
    created_at: datetime | None
    longitude: float
    latitude: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DisabledParking:
        """Return a DisabledParking object from a dictionary.

        Args:
            data: The data from the API.

        Returns:
            A DisabledParking object.
        """

        attr = data["properties"]
        geo = data["geometry"]["coordinates"]
        return cls(
            entry_id=attr.get("OBJECTID"),
            number=attr.get("AANTAL_PLAATSEN"),
            color=attr.get("KLEUR"),
            address=attr.get("ADRES"),
            gis_id=attr.get("GISID"),
            created_at=fromtimestamp(attr.get("START_DATE")),
            longitude=geo[0],
            latitude=geo[1],
        )


def fromtimestamp(epoch_time: int, default: None = None) -> Any:
    """Fromtimestamp function with default value.

    Args:
        epoch_time: The time in epoch format.
        default: The default value.

    Returns:
        The datetime object.
    """
    try:
        return datetime.fromtimestamp(epoch_time / 1000)
    except (ValueError, TypeError):
        return default
