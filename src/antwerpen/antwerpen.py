"""Asynchronous Python client providing Open Data information of Antwerpen."""
from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any

import async_timeout
from aiohttp import ClientError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .exceptions import ODPAntwerpenConnectionError, ODPAntwerpenError
from .models import DisabledParking


@dataclass
class ODPAntwerpen:
    """Main class for handling data fetchting from Open Data Platform of Antwerpen."""

    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to the Open Data Platform API of Antwerpen.

        Args:
        ----
            uri: Request URI, without '/', for example, 'status'
            method: HTTP method to use, for example, 'GET'
            params: Extra options to improve or limit the response.

        Returns:
        -------
            A Python dictionary (text) with the response from
            the Open Data Platform API.

        Raises:
        ------
            ODPAntwerpenConnectionError: Timeout occurred while
                connecting to the Open Data Platform API.
            ODPAntwerpenError: If the data is not valid.
        """
        version = metadata.version(__package__)
        url = URL.build(
            scheme="https",
            host="geodata.antwerpen.be",
            path="/arcgissql/rest/services/P_Portal/",
        ).join(URL(uri))

        headers = {
            "Accept": "application/geo+json",
            "User-Agent": f"PythonODPAntwerpen/{version}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    ssl=True,
                )
                response.raise_for_status()
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Open Data Platform API."
            raise ODPAntwerpenConnectionError(msg) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with Open Data Platform API."
            raise ODPAntwerpenConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/geo+json" not in content_type:
            text = await response.text()
            msg = "Unexpected content type response from the Open Data Platform API."
            raise ODPAntwerpenError(
                msg,
                {"Content-Type": content_type, "Response": text},
            )

        return await response.json()

    async def disabled_parkings(self, limit: int = 10) -> list[DisabledParking]:
        """Get all disabled parking spaces.

        Args:
        ----
            limit: Number of items to return.

        Returns:
        -------
            A list of DisabledParking objects.
        """
        results: list[DisabledParking] = []
        for offset in [0, 1000]:
            locations = await self._request(
                "portal_publiek6/MapServer/585/query",
                params={
                    "where": "1=1",
                    "resultOffset": offset,
                    "outFields": "*",
                    "f": "geojson",
                },
            )
            for location in locations["features"]:
                results.append(DisabledParking.from_dict(location))  # noqa: PERF401
        return results[:limit]

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> ODPAntwerpen:
        """Async enter.

        Returns
        -------
            The Open Data Platform object.
        """
        return self

    async def __aexit__(self, *_exc_info: str) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.
        """
        await self.close()
