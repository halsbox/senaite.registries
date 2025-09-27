SENAITE Registries
==================

senaite.registries provides a lightweight framework to manage laboratory registries in SENAITE LIMS.

It introduces:
- A top-level Registries container for all registries
- Pluggable, Dexterity-based registry types
- A Journal Registry with Journal entries as a first reference implementation
- A JSON API for programmatic import


Features
========

- RegistriesRootFolder
  - Top-level container for all registries

- Journal Registry (reference implementation)
  - Container for Journal entries
  - Listing with key fields and actions
  - Journal DX Type with fields:
    - Number (1..100, required)
    - Start/End Dates (date-only)
    - Responsible user (single user)
    - Storage Locations: active, pre-archive, archive (single-valued)

- JSON Import API
  - Programmatic import endpoint for batch creation of Journal entries
  - Accepts JSON payload, supports dry-run mode
  - Robust lookups:
    - Responsible: resolution by userid or via user search semantics
    - Storage: resolution by UID, path, id, or title (non-UID)

- Users/Lookup Utilities
  - users_search endpoint (JSON), used by widgets and API for user resolution


Installation
============

1) Add to your buildout and re-run buildout
   - Add senaite.registries to your instance buildout (eggs section)
   - Re-run buildout and restart the instance

2) Install in Plone via Add-ons (Site Setup → Add-ons)
   - The GenericSetup profile registers:
     - Browser layer
     - Dexterity FTIs
     - Static resources
     - Theme icon provider

3) Site structure is created on install
   - A Registries root folder at: /senaite_registries
   - A Journal Registry inside: /senaite_registries/journals
   - Items are (re)indexed to ensure they appear in navigation and listings


Uninstallation
==============

- Use Add-ons → Uninstall
- The uninstall profile:
  - Removes FTIs, browser layer registrations
  - Cleans nav visibility settings
  - Hard-uncatalogs the registries subtree from core catalogs (safe even if FTIs are gone)

Run with Docker
=======================

An example Docker Compose file is provided under ``docker/compose.yml`` to run SENAITE with this add-on.

Usage
=====

Journals Registry
-----------------

- Navigate to: Registries → Journals
- Add Journal objects via the standard Add menu
- Fields:
  - Number: integer 1..100
  - Start/End Date: date-only
  - Responsible: single user (select via user search widget)
  - Storage (Active/Pre-archive/Archive):
    - Single StorageLocation reference each (UIDReference)
    - Choices pulled from SETUP_CATALOG with active sorting


JSON Import API
===============

Overview
--------

- Endpoint (per Journal Registry):
  - POST {registry}/journal_import_api
  - Example: https://<host>/<site>/senaite_registries/journals/journal_import_api
- Content-Type: application/json
- Permission: cmf.AddPortalContent on the target Journal Registry
- CSRF: disabled for this endpoint (API-only usage)
- Dry-run: "?dry_run=true" querystring


Payload
-------

- Array of items:

.. code-block:: json

  [
    {
      "title": "Batch Register 1",
      "description": "optional",
      "number": 1,
      "start_date": "2025-01-01",
      "end_date": "2025-02-01",
      "responsible": "labmanager",
      "storage_active": "UID-OR-TITLE-OR-PATH",
      "storage_pre": "Cold Room A",
      "storage_archive": "/setup/storage/archive-1"
    }
  ]

- Or object with items:

.. code-block:: json

  {
    "items": [
      { "...": "..." }
    ]
  }


Field semantics
---------------

- title: required, Journal title
- number: required integer (1..100)
- start_date: required; parsed with SENAITE date parsing (e.g. 2025-01-31, 31/01/2025)
- end_date: optional; must not be earlier than start_date
- responsible: required; may be:
  - exact userid, or
  - any query that resolves via the SENAITE users search logic (see below)
- storage_active, storage_pre, storage_archive:
  - may be a StorageLocation UID, absolute/portal-relative path, id, or title
  - active is required; others optional
  - ambiguous matches raise an error


Lookups
-------

- Responsible resolution (reuses users search semantics):
  1) exact userid
  2) Users search by query
  3) Users search by wildcard "*query*"
  - If exactly one match → resolved
  - If none → error
  - If multiple → ambiguous error

- Storage resolution:
  1) by UID
  2) by traversal (absolute or portal-relative path)
  3) by id or title via SETUP_CATALOG
     - exact id/title
     - case-insensitive exact title
     - unique partial title match
  - If none or ambiguous (and field required) → error


Response
--------

- Status:
  - 200 OK if all items succeeded
  - 207 Multi-Status if some failed
- Body:

.. code-block:: json

  {
    "processed": 2,
    "created": 2,
    "errors": 0,
    "dry_run": false,
    "results": [
      {"index": 0, "status": "ok", "message": "Created: Batch Register 1", "url": "https://.../batch-register-1"},
      {"index": 1, "status": "ok", "message": "Created: Batch Register 2", "url": "https://.../batch-register-2"}
    ]
  }


Example (curl)
--------------

.. code-block:: shell

  curl -X POST \
    -H "Content-Type: application/json" \
    "https://<host>/<site>/senaite_registries/journals/journal_import_api?dry_run=true" \
    --data-binary @/path/to/journals.json


Users Search Endpoint
=====================

- Utility endpoint used by widgets and the API to resolve users.
- URL:
  - GET @@users_search/search?q=<query>&limit=<n>&b_start=<offset>
- Response:

.. code-block:: json

  {
    "items": [{"id": "labmanager", "fullname": "Lab Manager"}, ...],
    "count": 1,
    "page": 1,
    "pages": 1,
    "next": "",
    "previous": ""
  }


Internationalization
====================

- i18n domain: senaite.registries
- Translations are under locales/


Extensibility and Roadmap
=========================

This add-on is designed to host multiple registries. The Journal Registry is the first concrete example. Future work may include:

- Additional registries (e.g. QC SOPs)
- Unified import/export JSON endpoints across registries


License
=======

- see LICENSE