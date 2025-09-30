# SENAITE Registries
[Russian README](README.ru.md)

Lightweight framework to manage laboratory registries in SENAITE LIMS.

## What you get

- A top-level Registries container for all registries
- A Journal Registry with Journal entries
- JSON Import API for batch creation
- Users search endpoint for widgets and API lookups

## Quick start

### Install
- Add senaite.registries to your buildout (eggs) and re-run buildout
- Install via Site Setup → Add-ons

### Usage
- Navigate to: Registries → Journals
- Add Journal objects via the standard Add menu
- Change the state and edit Journal objects via the standard content menu

## Run with Docker

An example Docker Compose file is provided under `docker/compose.yml` to run SENAITE with this add-on.

## Journal Registry

### Fields
- Title (required)
- Description (optional)
- Number (1..100, required)
- Start/End Dates
- Responsible
- Storage:
  - Active
  - Pre-archive
  - Archive
- Attachment (optional)

## Journal lifecycle

### States
- New: Just created
- Active: In use
- Pre-archive: Ended and awaiting archiving
- Archived: Final state

### Actions
- Start Using: moves New → Active
- End Using: moves Active → Pre-archive
- Archive: moves Pre-archive → Archived
- Unarchive: moves Archived → Pre-archive

### Hints
- Start date is set automatically when you “Start Using” (if not set)
- End date is set automatically when you “End Using” (if not set)

## Import Journals (optional)

- POST JSON to: `/senaite_registries/journals/journal_import_api`
- Optional dry run: `?dry_run=true`
- Minimal example:

```json

  [
    {
      "title": "Batch Register 1",
      "number": 1,
      "start_date": "2025-01-01",
      "responsible": "labmanager",
      "storage_active": "Cold Room A"
    }
  ]
```

- The importer resolves users (by id or name) and storage (by UID, path, id, or title)
- Response includes per-item status and URLs of created items

## Roles and permissions

| Permission                 | LabClerk | LabManager | Manager |
|---------------------------|:--------:|:----------:|:-------:|
| Manage Registries         |          |     X      |    X    |
| Add Journal               |    X     |     X      |    X    |
| Edit “Responsible” field  |          |     X      |    X    |
| Start Using / End Using   |    X     |     X      |    X    |
| Archive                   |          |     X      |    X    |
| Unarchive                 |          |            |    X    |

## Roadmap

- Additional registries beyond Journals
- Unified import/export across registries

## Compatibility

- Requires SENAITE 2.6+

## License

- see LICENSE
