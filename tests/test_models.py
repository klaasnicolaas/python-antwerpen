"""Test the models."""
from aiohttp import ClientSession
from aresponses import ResponsesMockServer

from antwerpen import DisabledParking, ODPAntwerpen

from . import load_fixtures


async def test_all_disabled_parking_spaces(aresponses: ResponsesMockServer) -> None:
    """Test all disabled parking spaces function."""
    aresponses.add(
        "geodata.antwerpen.be",
        "/arcgissql/rest/services/P_Portal/portal_publiek6/MapServer/585/query",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/geo+json"},
            text=load_fixtures("disabled_parking.geojson"),
        ),
    )
    async with ClientSession() as session:
        client = ODPAntwerpen(session=session)
        spaces: list[DisabledParking] = await client.disabled_parkings()
        assert spaces is not None
        for item in spaces:
            assert isinstance(item, DisabledParking)
            assert item.entry_id is not None
            assert item.coordinates is not None
            assert isinstance(item.coordinates, list)
