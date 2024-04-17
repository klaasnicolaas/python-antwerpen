"""Fixtures for the Antwerpen tests."""

from collections.abc import AsyncGenerator

import pytest
from aiohttp import ClientSession

from antwerpen import ODPAntwerpen


@pytest.fixture(name="odp_antwerpen_client")
async def client() -> AsyncGenerator[ODPAntwerpen, None]:
    """Create a client for the Antwerpen ODP."""
    async with (
        ClientSession() as session,
        ODPAntwerpen(session=session) as odp_antwerpen_client,
    ):
        yield odp_antwerpen_client
