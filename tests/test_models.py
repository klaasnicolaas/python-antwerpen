"""Test the models."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from antwerpen import DisabledParking
from antwerpen.models import fromtimestamp

from . import load_fixtures

if TYPE_CHECKING:
    from antwerpen import ODPAntwerpen


async def test_all_disabled_parking_spaces(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_antwerpen_client: ODPAntwerpen,
) -> None:
    """Test all disabled parking spaces function."""
    datasets: list[str] = [
        "disabled_parking.geojson",
        "disabled_parking.geojson",
    ]
    for dataset in datasets:
        aresponses.add(
            "geodata.antwerpen.be",
            "/arcgissql/rest/services/P_Portal/portal_publiek6/MapServer/585/query",
            "GET",
            aresponses.Response(
                status=200,
                headers={"Content-Type": "application/geo+json"},
                text=load_fixtures(dataset),
            ),
        )
    spaces: list[DisabledParking] = await odp_antwerpen_client.disabled_parkings()
    assert spaces == snapshot


@pytest.mark.parametrize(
    ("epoch", "expected", "fold"),
    [
        (1704067200000, "2024-01-01T01:00:00+01:00", 0),
        (1704067200123, "2024-01-01T01:00:00.123000+01:00", 0),
        (1719792000000, "2024-07-01T02:00:00+02:00", 0),
        (1729989000000, "2024-10-27T02:30:00+02:00", 0),
        (1729992600000, "2024-10-27T02:30:00+01:00", 1),
    ],
)
def test_source_timestamp_retains_brussels_time(
    epoch: int, expected: str, fold: int
) -> None:
    """Preserve milliseconds and winter/summer offsets, including repeated hours."""
    value = fromtimestamp(epoch)
    assert value.isoformat() == expected
    assert value.timestamp() * 1000 == epoch
    assert value.fold == fold


@pytest.mark.parametrize("epoch", [None, "invalid"])
def test_missing_or_invalid_source_timestamp(epoch: object) -> None:
    """Preserve the existing unknown-date behavior."""
    record = json.loads(load_fixtures("disabled_parking.geojson"))["features"][0]
    record["properties"]["EBDD"] = epoch
    assert DisabledParking.from_dict(record).created_at is None
