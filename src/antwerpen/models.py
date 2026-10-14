"""Asynchronous Python client providing Open Data information of Antwerpen."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo


@dataclass
class DisabledParking:
    """Object representing a disabled parking."""

    entry_id: int
    number: int
    orientation: str
    destiny: str
    window_time: str | None
    lined: bool
    status: str
    gis_id: str
    created_at: datetime | None
    coordinates: list[float]

    @classmethod
    def from_dict(cls: type[DisabledParking], data: dict[str, Any]) -> DisabledParking:
        """Return a DisabledParking object from a dictionary.

        Args:
        ----
            data: The data from the API.

        Returns:
        -------
            A DisabledParking object.

        """
        attr = data["properties"]
        return cls(
            entry_id=attr.get("OBJECTID"),
            number=attr.get("Capaciteit"),
            orientation=attr.get("Orientatie"),
            destiny=attr.get("Bestemming"),
            window_time=attr.get("VENSTERTIJD_BESCHR"),
            lined=attr.get("GELIJND") == "Ja",
            status=attr.get("STATUS"),
            gis_id=attr.get("GISID"),
            created_at=fromtimestamp(attr.get("EBDD")),
            coordinates=data["geometry"]["coordinates"][0],
        )


def fromtimestamp(epoch_time: int, default: None = None) -> Any:
    """Fromtimestamp function with default value.

    Args:
    ----
        epoch_time: The time in epoch format.
        default: The default value.

    Returns:
    -------
        The datetime object.

    """
    try:
        return datetime.fromtimestamp(
            epoch_time / 1000,
            tz=ZoneInfo("Europe/Brussels"),
        )
    except (ValueError, TypeError):
        return default


@dataclass
class ParkingRecord:
    """Original GIS identity, full WGS84 area and unmodified source claims."""

    id: str
    geometry: dict[str, Any]
    source_attributes: dict[str, Any]


@dataclass
class ParkingCollection:
    """Evidence for a complete selection, never a truncated inspection list."""

    records: list[ParkingRecord]
    total_count: int
    pages_fetched: int
    source_version: str | None
    complete: bool = True
