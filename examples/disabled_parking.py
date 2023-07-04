# pylint: disable=W0621
"""Asynchronous Python client providing Open Data information of Antwerpen."""

import asyncio

from antwerpen import ODPAntwerpen


async def main() -> None:
    """Show example on using the Antwerpen API client."""
    async with ODPAntwerpen() as client:
        disabled_parkings = await client.disabled_parkings(limit=100)

        count = len(disabled_parkings)
        for item in disabled_parkings:
            print(item)

        # Count unique id's in disabled_parkings
        unique_values = len({item.entry_id for item in disabled_parkings})

        print("__________________________")
        print(f"Total locations found: {count}")
        print(f"Unique ID values: {unique_values}")


if __name__ == "__main__":
    asyncio.run(main())
