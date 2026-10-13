"""Asynchronous Python client providing Open Data information of Antwerpen."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import ClientError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .exceptions import ODPAntwerpenConnectionError, ODPAntwerpenError
from .models import DisabledParking, ParkingCollection, ParkingRecord

VERSION: str = metadata.version("antwerpen")


@dataclass
class ODPAntwerpen:
    """Main class for handling data fetching from Open Data Platform of Antwerpen."""

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
        url = URL.build(
            scheme="https",
            host="geodata.antwerpen.be",
            path="/arcgissql/rest/services/P_Portal/",
        ).join(URL(uri))

        headers = {
            "Accept": "application/geo+json",
            "User-Agent": f"PythonODPAntwerpen/{VERSION}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    ssl=True,
                )
                response.raise_for_status()
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Open Data Platform API."
            raise ODPAntwerpenConnectionError(msg) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with Open Data Platform API."
            raise ODPAntwerpenConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")
        if not any(
            value in content_type
            for value in ("application/geo+json", "application/json")
        ):
            text = await response.text()
            msg = "Unexpected content type response from the Open Data Platform API."
            raise ODPAntwerpenError(
                msg,
                {"Content-Type": content_type, "Response": text},
            )

        try:
            data = await response.json()
        except ValueError as exception:
            msg = "Invalid JSON from the Open Data Platform API."
            raise ODPAntwerpenError(msg) from exception
        if not isinstance(data, dict) or "error" in data:
            msg = "Invalid or failed ArcGIS response."
            raise ODPAntwerpenError(msg)
        return data

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

    async def parking_collection(
        self, *, set_filter: str | None = None, max_records: int = 10000
    ) -> ParkingCollection:
        """Retrieve the entire layer, checking counts, IDs and repeated source claims.

        GISID is the publisher's identity; OBJECTID only orders pagination. No
        verified dataset revision is available. Two equal reads detect observed
        changes but do not establish a transactional snapshot or ID permanence.
        """
        if (
            isinstance(max_records, bool)
            or not isinstance(max_records, int)
            or max_records < 1
        ):
            msg = "max_records must be a positive integer"
            raise ValueError(msg)
        where = set_filter or "1=1"
        total = await self._parking_count(where)
        if total > max_records:
            msg = "Parking selection exceeds the safety ceiling"
            raise ODPAntwerpenError(msg)
        first, pages = await self._parking_records(total, where)
        second, repeated_pages = await self._parking_records(total, where)
        if await self._parking_count(where) != total or first != second:
            msg = "Parking selection changed during retrieval"
            raise ODPAntwerpenError(msg)
        return ParkingCollection(first, total, pages + repeated_pages, None)

    async def _parking_count(self, where: str) -> int:
        """Read the source count independently of retrieved pages."""
        data = await self._request(
            "portal_publiek6/MapServer/585/query",
            params={"where": where, "returnCountOnly": "true", "f": "json"},
        )
        count = data.get("count")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            msg = "Invalid parking selection count"
            raise ODPAntwerpenError(msg)
        return count

    async def _parking_records(
        self, total: int, where: str
    ) -> tuple[list[ParkingRecord], int]:
        """Read bounded ordered pages and reject incomplete or duplicated IDs."""
        records: list[ParkingRecord] = []
        seen: set[str] = set()
        object_ids: set[int] = set()
        pages = 0
        for offset in range(0, max(total, 1), 500):
            data = await self._request(
                "portal_publiek6/MapServer/585/query",
                params={
                    "where": where,
                    "resultOffset": offset,
                    "resultRecordCount": 500,
                    "orderByFields": "OBJECTID ASC",
                    "outFields": "*",
                    "outSR": 4326,
                    "f": "geojson",
                },
            )
            features = data.get("features")
            if (
                data.get("type") != "FeatureCollection"
                or not isinstance(features, list)
                or len(features) != min(500, total - offset)
            ):
                msg = "Incomplete parking page"
                raise ODPAntwerpenError(msg)
            pages += 1
            for feature in features:
                if (
                    not isinstance(feature, dict)
                    or not isinstance(feature.get("properties"), dict)
                    or not isinstance(feature.get("geometry"), dict)
                ):
                    msg = "Invalid parking feature"
                    raise ODPAntwerpenError(msg)
                attributes = feature["properties"]
                spot_id = attributes.get("GISID")
                object_id = attributes.get("OBJECTID")
                if (
                    not isinstance(spot_id, str)
                    or not spot_id
                    or spot_id != spot_id.strip()
                    or spot_id in seen
                    or isinstance(object_id, bool)
                    or not isinstance(object_id, int)
                    or object_id in object_ids
                ):
                    msg = "Missing or duplicate parking identity"
                    raise ODPAntwerpenError(msg)
                seen.add(spot_id)
                object_ids.add(object_id)
                records.append(ParkingRecord(spot_id, feature["geometry"], attributes))
            if len(records) == total and data.get("exceededTransferLimit"):
                msg = "Parking response has remaining records"
                raise ODPAntwerpenError(msg)
        return records, pages

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The Open Data Platform object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
