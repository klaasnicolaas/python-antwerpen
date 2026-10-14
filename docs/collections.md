# Complete parking collections

[Back to the README](../README.md)

`await client.parking_collection(set_filter=None, max_records=10000)` returns `ParkingCollection(records, total_count, pages_fetched, source_version=None, complete=True)`. Each `ParkingRecord` preserves its original `GISID` as `id`, full WGS84 `geometry` (including all rings), and unmodified `source_attributes`. The existing capped `disabled_parkings()` inspection API remains compatible.

The client reads the source count, ordered 500-record pages twice, and the final count. Short pages, duplicate/missing GIS IDs or OBJECTIDs, observed source edits, ArcGIS errors and safety-ceiling overflow raise `ODPAntwerpenError`; no partial collection is returned. Empty selections can be proven complete. Two identical reads are change detection, not a transactional snapshot. GISID continuity is not guaranteed by the publisher; OBJECTID only orders retrieval.

The public layer contains one record without GISID as checked on 2026-10-13. The default full collection rejects it. Consumers explicitly choosing an identified subset can pass `set_filter="GISID IS NOT NULL AND GISID <> ''"`; this changes coverage and must be disclosed. The identified subset contained 1,847 records (eight page reads); the full layer contained 1,848.

Layer metadata describes polygons from the paid-parking-area inventory (2018), not verified citywide coverage or present availability. All inspected records say `toegang=Beperkt`, and 25 contain time-window claims despite the layer description saying no time-window regime. Preserve those claims rather than inferring unrestricted or personal access. `EBDD` and portal modification times are not verified record-update timestamps. Data rights differ from this client's MIT licence: see the [city's open-data terms](https://www.antwerpen.be/info/gratis-open-data-licentie) and [publisher item](https://www.arcgis.com/home/item.html?id=3b69e4d15fc14fbb86a00d6c636da475).
