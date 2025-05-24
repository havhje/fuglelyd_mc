# Artskart Public API Guide

This document provides a summary of the Artskart Public API capabilities, based on the Swagger v1 documentation.
The base URL for this API is: `https://artskart.artsdatabanken.no/publicapi/api`

## API Endpoints

The API is organized into several sections:

### 1. DarwinCoreCache

This section provides access to Darwin Core records.

*   **`GET /api/darwincorecache/stats/{nodeId}/{includeDeleted}`**
    *   **Description**: Get statistics for a node (e.g., number of records, max track date).
    *   **Parameters**:
        *   `nodeId` (path, integer, required): Nodedatabase Id.
        *   `includeDeleted` (path, boolean, required): Whether to include deleted records.
    *   **Response**: JSON object with `NumberOfRecords` and `MaxTrackDateTime`.

*   **`GET /api/darwincorecache/list/{nodeId}/{pageIndex}/{pageSize}/{includeDeleted}`**
    *   **Description**: Gets a paginated list of all DarwinCoreRecords for a node.
    *   **Parameters**:
        *   `nodeId` (path, integer, required): Nodedatabase Id.
        *   `pageIndex` (path, integer, required): Page index (zero-based).
        *   `pageSize` (path, integer, required): Number of records per page.
        *   `includeDeleted` (path, boolean, required): Whether to include deleted records.
    *   **Response**: A JSON array of Darwin Core record objects. Each object contains detailed information such as `ScientificName`, `NorskNavn` (Norwegian Name), `Family`, `Order`, `Class`, `Kingdom`, `EventDate`, `Locality`, `Latitude`, `Longitude`, `Multimedias`, etc.

*   **`GET /api/darwincorecache/list/afterdatetime/{nodeId}/{afterDateTime}/{pageSize}/{includeDeleted}`**
    *   **Description**: Gets a list of DarwinCoreRecords for a node created or updated after a specific datetime.
    *   **Parameters**:
        *   `nodeId` (path, integer, required): Nodedatabase Id.
        *   `afterDateTime` (path, string, required): ISO 8601 datetime string.
        *   `pageSize` (path, integer, required): Number of records per page.
        *   `includeDeleted` (path, boolean, required): Whether to include deleted records.
    *   **Response**: A JSON array of Darwin Core record objects.

*   **`GET /api/darwincorecache/currentids/{nodeId}/{pageIndex}/{pageSize}`**
    *   **Description**: Gets a paginated list of all current DarwinCoreRecordIds for a node.
    *   **Parameters**:
        *   `nodeId` (path, integer, required): Nodedatabase Id.
        *   `pageIndex` (path, integer, required): Page index (zero-based).
        *   `pageSize` (path, integer, required): Number of records per page.
    *   **Response**: A JSON array of strings (record IDs).

*   **`GET /api/darwincorecache/deleted/{nodeId}/{afterDateTime}/{pageIndex}/{pageSize}`**
    *   **Description**: Gets a paginated list of deleted DarwinCoreRecordIds for a node after a specific datetime.
    *   **Parameters**:
        *   `nodeId` (path, integer, required): Nodedatabase Id.
        *   `afterDateTime` (path, date-time, required): ISO 8601 datetime string.
        *   `pageIndex` (path, integer, required): Page index (zero-based).
        *   `pageSize` (path, integer, required): Number of records per page.
    *   **Response**: A JSON array of strings (record IDs).

*   **`GET /api/darwincorecache/{id}`**
    *   **Description**: Get a single Darwin Core record by its ID.
    *   **Parameters**:
        *   `id` (path, string, required): Record ID (e.g., "urn:catalog:o:l:38").
    *   **Response**: A JSON object representing a single Darwin Core record.

*   **`GET /api/darwincorecache/history/{id}`**
    *   **Description**: Get the history of a single Darwin Core record by its ID.
    *   **Parameters**:
        *   `id` (path, string, required): Record ID (e.g., "O/L/1").
    *   **Response**: A JSON object with a `History` array containing record versions, `Id`, `IsComplete`, and `TimeStamp`.

### 2. Image

This section provides access to thumbnail images.

*   **`GET /api/Image/{id}`**
    *   **Description**: Fetch a thumbnail image.
    *   **Parameters**:
        *   `id` (path, string, required): The thumbnail ID. Note: If the ID contains '/', it must be URL encoded or passed as a query parameter `?id=...`.
    *   **Response**: JSON object containing image headers. (The actual image is likely served directly, and headers provide metadata).

### 3. ListHelper & ListHelperV2

These sections provide tools for aggregating and retrieving observation data, particularly for lists and area calculations. `ListHelperV2` appears to be an updated version with more filter options.

*Common Parameters for ListHelper/ListHelperV2 endpoints (query parameters unless noted):*
    *   `id` (path, integer, required): Typically a taxon ID or similar identifier for the list.
    *   `fromYear`, `toYear`, `fromMonth` (V2), `toMonth` (V2): Date range filters.
    *   `region`, `type`, `geojsonPolygon`, `addPoints`, `removePoints`: Geographical and type filters.
    *   `scientificNameId`: Filter by scientific name ID.
    *   `sourcedatabases`: Filter by source databases.
    *   `crs`: Coordinate Reference System.
    *   `countyYear` (V2): Specify year for county definitions.
    *   `hidden` (V2, boolean), `quality` (V2, boolean): Additional filters for V2.

*   **`GET /api/listhelper/{id}/countylist`** and **`GET /api/listhelper/v2/{id}/countylist`**
    *   **Description**: Aggregate county presence for a taxon.
    *   **Response**: JSON array of objects, each with `KOMM` (municipality number), `NAVN` (name), and `Status`.

*   **`GET /api/listhelper/{id}/areadata`** and **`POST /api/listhelper/{id}/areadata`**
*   **`GET /api/listhelper/v2/{id}/areadata`** and **`POST /api/listhelper/v2/{id}/areadata`**
    *   **Description**: Aggregate area data for a taxon (Area of Occupancy, Extent of Occurrence, etc.).
    *   **Response**: JSON object with `TaxonId`, `AreaOfOccupancy`, `AreaExtentOfOccurrence`, `IndividualCount`, `NumberOfRecords`, etc.

*   **`GET /api/listhelper/{id}/observations`** and **`POST /api/listhelper/{id}/observations`**
*   **`GET /api/listhelper/v2/{id}/observations`** and **`POST /api/listhelper/v2/{id}/observations`**
    *   **Description**: Retrieve observations based on the provided filters.
    *   **Response**: JSON object (structure might vary, example shows `{}`).

*   **`GET /api/listhelper/{id}/downloadObservations`** and **`POST /api/listhelper/{id}/downloadObservations`**
*   **`GET /api/listhelper/v2/{id}/downloadObservations`** and **`POST /api/listhelper/v2/{id}/downloadObservations`**
    *   **Description**: Prepare observations for download based on filters.
    *   **Response**: JSON object (structure might vary, example shows `{}`).

### 4. Lookup

Provides access to predefined lookup lists (controlled vocabularies).

*   **`GET /api/lookup/{context}`**
    *   **Description**: Fetch a lookup list for a specific context.
    *   **Parameters**:
        *   `context` (path, string, required): Context, e.g., `geoprecision`, `activity`, `taxongroup`, `status`.
    *   **Response**: JSON array of lookup objects, each with `Context`, `Key`, `Value`, and `ValueList`.

*   **`GET /api/Lookup`**
    *   **Description**: Gets all lookup lists.
    *   **Response**: JSON array of lookup objects.

### 5. Observations

This section allows fetching detailed observation data.

*   **`GET /api/observations/{id}`**
    *   **Description**: Get a single observation by its Darwin Core ID.
    *   **Parameters**:
        *   `id` (path, string, required): Darwin Core ID (format: InstitutionCode/Collectioncode/CatalogNumber).
        *   `crs` (query, string, optional): EPSG code for coordinate projection of the result.
    *   **Response**: A detailed JSON object for the observation, including `species`, `ScientificName`, `Collector`, `CollectedDate`, `Locality`, `Longitude`, `Latitude`, `ThumbImgUrls`, etc.

*   **`GET /api/observations/list`**
    *   **Description**: Gets a paginated list of observations based on a complex filter object.
    *   **Parameters (主な query parameters for `filter.`):**
        *   `pageIndex`, `pageSize` (query, integer): For pagination.
        *   `crs` (query, string, optional): EPSG code for coordinate projection.
        *   `filter.scientificNameIds` (array of integers): Filter by scientific name IDs.
        *   `filter.areas` (array of strings): Area filter (e.g., municipality IDs).
        *   `filter.basisOfRecords` (array of strings): Filter by basis of record.
        *   `filter.fromDate`, `filter.toDate` (string): Date range for collection.
        *   `filter.wktPolygon` (string): WKT polygon for spatial filtering.
        *   Many other filter options available (see Swagger for full list).
    *   **Response**: JSON object containing an `Observations` array, `PageIndex`, `PageSize`, `TotalCount`, `TotalPages`. Each observation in the array is detailed.

*   **`GET /api/observations/listall`**
    *   **Description**: Similar to `/api/observations/list` but retrieves all matching observations without pagination (can lead to timeouts for large queries).
    *   **Parameters**: Same filter parameters as `/api/observations/list`.
    *   **Response**: A JSON array of detailed observation objects.

*   **`GET /api/observations/Deleted`**
    *   **Description**: Gets a list of IDs of deleted observations after a specific track datetime.
    *   **Parameters**:
        *   `afterTrackDateTime` (query, date-time, required).
        *   `pageIndex`, `pageSize` (query, integer): For pagination.
    *   **Response**: JSON object with `ObservationIds` array and pagination info.

### 6. Ping

A simple health check endpoint.

*   **`GET /api/ping`**
    *   **Description**: Checks if the API is responsive.
    *   **Response**: A string (likely "pong" or similar indicating service is up).

### 7. Taxon

This section is used to fetch taxonomic information. This is the primary section used by the `artskart_api.py` module in this project.

*   **`GET /api/taxon/{id}/short`**
    *   **Description**: Get short information on a taxon by its internal integer ID.
    *   **Parameters**:
        *   `id` (path, integer, required): Taxon ID.
    *   **Response**: JSON object with `Id` (string version of intId), `IntId`, `PopularName`, `MatchedName`, `ScientificName`, `ScientificNameFormatted`, `ScientificNameAuthorship`.

*   **`GET /api/taxon/{id}`**
    *   **Description**: Get full information on a taxon by its internal integer ID.
    *   **Parameters**:
        *   `id` (path, integer, required): Taxon ID.
    *   **Response**: A detailed JSON object for the taxon, including:
        *   `Id` (integer, same as input `id`), `ValidScientificNameId`, `ValidScientificName`, `ValidScientificNameFormatted`, `ValidScientificNameAuthorship`.
        *   `PrefferedPopularname` (Norwegian popular name if available).
        *   `TaxonGroup`, `TaxonGroupId`.
        *   `ScientificNames` (list of scientific names, including synonyms, with `Accepted` status).
        *   `PopularNames` (list of popular names in different languages, with `language` and `Preffered` flag).
        *   Hierarchy: `Kingdom`, `Phylum`, `Class`, `Order`, `Family`, `Genus`, `Species`, `SubSpecies`.
        *   `Status` (e.g., red list status).

*   **`GET /api/taxon`**  **(Currently used by `fetch_artskart_taxon_info_by_name`)**
    *   **Description**: Get a list of taxon information based on a search term and optional filters.
    *   **Parameters**:
        *   `term` (query, string, required): The search term (e.g., a scientific name or popular name).
        *   `taxonGroups` (query, string, optional): Comma-separated list of taxon group IDs to filter by.
        *   `statuses` (query, string, optional): Comma-separated list of status codes (e.g., 'hi,cr,en' for red list).
        *   `take` (query, integer, optional): Number of results to return (default 15, -1 for all).
    *   **Response**: A JSON array of detailed taxon objects (same structure as `GET /api/taxon/{id}`). The current project script iterates through this list to find the best match.

*   **`GET /api/taxon/short`**
    *   **Description**: Get a list of short taxon information based on search criteria.
    *   **Parameters**: Same as `GET /api/taxon` (`term`, `taxonGroups`, `statuses`).
    *   **Response**: A JSON array of short taxon info objects (same structure as `GET /api/taxon/{id}/short`).

*   **`GET /api/taxon/{id}/children`**
    *   **Description**: Get a list of children (full info) for a parent taxon ID.
    *   **Parameters**:
        *   `id` (path, integer, required): Parent taxon ID.
    *   **Response**: A JSON array of detailed taxon objects for children.

*   **`GET /api/taxon/{id}/children/short`**
    *   **Description**: Get a list of children (short info) for a parent taxon ID.
    *   **Parameters**:
        *   `id` (path, integer, required): Parent taxon ID.
    *   **Response**: A JSON array of short taxon info objects for children.

*   **`GET /api/taxon/scientificnameid`**
    *   **Description**: Get taxon information by its `ValidScientificNameId`.
    *   **Parameters**:
        *   `id` (query, integer, required): The `ValidScientificNameId`.
    *   **Response**: A JSON array containing one detailed taxon object if found.

*   **`GET /api/taxon/short/scientificnameid`**
    *   **Description**: Get short taxon information by its `ValidScientificNameId`.
    *   **Parameters**:
        *   `id` (query, integer, required): The `ValidScientificNameId`.
    *   **Response**: A JSON array containing one short taxon info object if found.

*   **`GET /api/Taxon`** (Note: This endpoint seems to have a different parameter structure in the Swagger, `taxonSearchParams.term` etc., compared to the `/api/taxon` used above. It might be an alternative or older way to search.)
    *   **Description**: Get a list (dictionary) of Taxons by search.
    *   **Parameters (using `taxonSearchParams.` prefix in query):**
        *   `taxonSearchParams.term` (string): Search term.
        *   `taxonSearchParams.statuses` (string): Filter by statuses.
        *   `taxonSearchParams.taxonGroups` (string): Filter by taxon groups.
        *   `taxonSearchParams.take` (integer): Number of results.
    *   **Response**: JSON object (example is `{}`, so structure is less clear from the provided doc).

## Key Data Points Currently Used by the Project:

From the `GET /api/taxon` (with `term` parameter) endpoint, the project primarily uses:
*   `ValidScientificName`: To confirm matches.
*   `ValidScientificNameId`: The unique ID for the taxon.
*   `PopularNames`: To extract Norwegian common names (`PrefferedPopularname` is often the direct Norwegian name, or logic is used to find "nb" language preferred names).
*   `Family`: Scientific name of the family.
*   `Order`: Scientific name of the order.

This guide should help in understanding the capabilities of the Artskart API and how the project currently interacts with it, as well as potential for future enhancements.
