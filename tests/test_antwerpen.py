"""Basic tests for the Open Data Platform API of Antwerpen."""

# pylint: disable=protected-access
import asyncio
from unittest.mock import patch

import pytest
from aiohttp import ClientError, ClientResponse, ClientSession
from aresponses import Response, ResponsesMockServer

from antwerpen import ODPAntwerpen
from antwerpen.exceptions import ODPAntwerpenConnectionError, ODPAntwerpenError

from . import load_fixtures


async def test_json_request(aresponses: ResponsesMockServer) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "geodata.antwerpen.be",
        "/arcgissql/rest/services/P_Portal/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/geo+json"},
            text=load_fixtures("disabled_parking.geojson"),
        ),
    )
    async with ClientSession() as session:
        client = ODPAntwerpen(session=session)
        response = await client._request("test")
        assert response is not None
        await client.close()


async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test internal session is handled correctly."""
    aresponses.add(
        "geodata.antwerpen.be",
        "/arcgissql/rest/services/P_Portal/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/geo+json"},
            text=load_fixtures("disabled_parking.geojson"),
        ),
    )
    async with ODPAntwerpen() as client:
        await client._request("test")


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout from the Open Data Platform API of Antwerpen."""

    # Faking a timeout by sleeping
    async def response_handler(_: ClientResponse) -> Response:
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body="Goodmorning!",
            text=load_fixtures("disabled_parking.geojson"),
        )

    aresponses.add(
        "geodata.antwerpen.be",
        "/arcgissql/rest/services/P_Portal/test",
        "GET",
        response_handler,
    )

    async with ClientSession() as session:
        client = ODPAntwerpen(
            session=session,
            request_timeout=0.1,
        )
        with pytest.raises(ODPAntwerpenConnectionError):
            assert await client._request("test")


async def test_content_type(aresponses: ResponsesMockServer) -> None:
    """Test request content type error from Open Data Platform API of Antwerpen."""
    aresponses.add(
        "geodata.antwerpen.be",
        "/arcgissql/rest/services/P_Portal/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "blabla/blabla"},
        ),
    )

    async with ClientSession() as session:
        client = ODPAntwerpen(session=session)
        with pytest.raises(ODPAntwerpenError):
            assert await client._request("test")


async def test_client_error() -> None:
    """Test request client error from the Open Data Platform API of Antwerpen."""
    async with ClientSession() as session:
        client = ODPAntwerpen(session=session)
        with (
            patch.object(
                session,
                "request",
                side_effect=ClientError,
            ),
            pytest.raises(ODPAntwerpenConnectionError),
        ):
            assert await client._request("test")
