"""Complete collection checks, independent of any downstream importer."""

from copy import deepcopy
from unittest.mock import AsyncMock, patch

import pytest

from antwerpen import ODPAntwerpen, ODPAntwerpenError


def feature(identity: str = "GIS_1", object_id: int = 1) -> dict:
    """Build a small original source area and claims."""
    return {
        "type": "Feature",
        "properties": {"GISID": identity, "OBJECTID": object_id, "Capaciteit": None},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[4.4, 51.2], [4.401, 51.2], [4.4, 51.201], [4.4, 51.2]]],
        },
    }


def page(*features: object) -> dict:
    """Build a GeoJSON page."""
    return {"type": "FeatureCollection", "features": list(features)}


async def test_complete_collection() -> None:
    """Check every page, source count, raw claims and explicit WGS84 request."""
    records = [feature(f"GIS_{index}", index) for index in range(501)]
    first, last = page(*records[:500]), page(records[-1])
    with patch.object(ODPAntwerpen, "_request", new_callable=AsyncMock) as request:
        request.side_effect = [{"count": 501}, first, last, first, last, {"count": 501}]
        result = await ODPAntwerpen().parking_collection(set_filter="GISID IS NOT NULL")
    assert all(
        call.kwargs["params"]["where"] == "GISID IS NOT NULL"
        for call in request.call_args_list
    )
    assert result.total_count == 501
    assert result.pages_fetched == 4
    assert result.complete
    assert result.source_version is None
    assert result.records[0].gis_id == "GIS_0"
    assert result.records[0].source_attributes == records[0]["properties"]
    assert result.records[0].geometry == records[0]["geometry"]
    assert request.call_args_list[1].kwargs["params"]["outSR"] == 4326
    assert request.call_args_list[2].kwargs["params"]["resultOffset"] == 500


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
async def test_invalid_ceiling(limit: int) -> None:
    """Reject invalid ceilings before any request."""
    with pytest.raises(ValueError, match="positive integer"):
        await ODPAntwerpen().parking_collection(max_records=limit)


@pytest.mark.parametrize("count", [None, True, -1, "1"])
async def test_invalid_count(count: object) -> None:
    """A received list length cannot replace source evidence."""
    with (
        patch.object(
            ODPAntwerpen,
            "_request",
            new_callable=AsyncMock,
            return_value={"count": count},
        ),
        pytest.raises(ODPAntwerpenError, match="count"),
    ):
        await ODPAntwerpen().parking_collection()


async def test_ceiling_does_not_truncate() -> None:
    """Do not retrieve or return an oversized partial selection."""
    with (
        patch.object(
            ODPAntwerpen, "_request", new_callable=AsyncMock, return_value={"count": 2}
        ) as request,
        pytest.raises(ODPAntwerpenError, match="ceiling"),
    ):
        await ODPAntwerpen().parking_collection(max_records=1)
    assert request.call_count == 1


@pytest.mark.parametrize(
    "response",
    [
        page(),
        {},
        {"type": "FeatureCollection", "features": None},
        page(None),
        page({"properties": {}, "geometry": None}),
        page({"properties": {}, "geometry": {}}),
        {**page(feature()), "exceededTransferLimit": True},
    ],
)
async def test_invalid_page(response: dict) -> None:
    """Reject missing rows, malformed features and remaining records."""
    with (
        patch.object(
            ODPAntwerpen,
            "_request",
            new_callable=AsyncMock,
            side_effect=[{"count": 1}, response],
        ),
        pytest.raises(ODPAntwerpenError),
    ):
        await ODPAntwerpen().parking_collection()


@pytest.mark.parametrize("second", [feature("GIS_1", 2), feature("GIS_2", 1)])
async def test_duplicate_identity(second: dict) -> None:
    """Both original GIS IDs and pagination OBJECTIDs must be unique."""
    with (
        patch.object(
            ODPAntwerpen,
            "_request",
            new_callable=AsyncMock,
            side_effect=[{"count": 2}, page(feature(), second)],
        ),
        pytest.raises(ODPAntwerpenError, match="identity"),
    ):
        await ODPAntwerpen().parking_collection()


async def test_observed_change() -> None:
    """Same-count edits must also prevent a complete collection."""
    changed = deepcopy(feature())
    changed["properties"]["Capaciteit"] = 2
    with (
        patch.object(
            ODPAntwerpen,
            "_request",
            new_callable=AsyncMock,
            side_effect=[{"count": 1}, page(feature()), page(changed), {"count": 1}],
        ),
        pytest.raises(ODPAntwerpenError, match="changed"),
    ):
        await ODPAntwerpen().parking_collection()


async def test_changed_count() -> None:
    """Refuse a count that changes after retrieval."""
    with (
        patch.object(
            ODPAntwerpen,
            "_request",
            new_callable=AsyncMock,
            side_effect=[{"count": 1}, page(feature()), page(feature()), {"count": 2}],
        ),
        pytest.raises(ODPAntwerpenError, match="changed"),
    ):
        await ODPAntwerpen().parking_collection()


async def test_complete_empty_collection() -> None:
    """The package can prove empty; consumers decide whether to accept it."""
    with patch.object(
        ODPAntwerpen,
        "_request",
        new_callable=AsyncMock,
        side_effect=[{"count": 0}, page(), page(), {"count": 0}],
    ):
        result = await ODPAntwerpen().parking_collection()
    assert result.complete
    assert result.total_count == 0
    assert result.records == []
