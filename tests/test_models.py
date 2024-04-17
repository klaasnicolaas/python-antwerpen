"""Test the models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from . import load_fixtures

if TYPE_CHECKING:
    from antwerpen import DisabledParking, ODPAntwerpen


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
