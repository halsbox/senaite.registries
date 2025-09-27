# -*- coding: utf-8 -*-
import json
from DateTime import DateTime
from Products.Five import BrowserView
from plone import api as ploneapi
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides

from bika.lims import api
from bika.lims.catalog import SETUP_CATALOG
from senaite.registries import logger
from senaite.registries.browser.common import normalize, json_default, get_bool, stringify_exception
from senaite.core.browser.usergroup.usergroups_usersoverview import UsersOverviewControlPanel
from six import string_types

REQUIRED_FIELDS = ("title", "number", "start_date", "responsible", "storage_active")
FIELDS = REQUIRED_FIELDS | (
    "description",
    "end_date",
    "storage_pre",
    "storage_archive",
)

def parse_payload(body):
  if not body:
    raise ValueError("Empty request body")
  data = body.read()
  if isinstance(data, bytes):
    data = data.decode("utf-8", "replace")
  try:
    payload = json.loads(data)
  except Exception:
    raise ValueError("Invalid JSON payload")
  if isinstance(payload, dict):
    items = payload.get("items", [])
    if not isinstance(items, list):
      raise ValueError("'items' must be a list")
    return items
  elif isinstance(payload, list):
    return payload
  else:
    raise ValueError("Unsupported payload type")

def parse_date(value, label):
  try:
    return dtime.to_DT(dtime.parse(value))
  except Exception:
    try:
      return DateTime(value)
    except Exception:
      raise ValueError(u"Invalid {}: '{}'".format(label, value))

def validate_and_normalize(row):
  if not isinstance(raw, dict):
    raise ValueError(u"Invalid row: {}".format(raw))
  missing = [f for f in REQUIRED_FIELDS if not row.get(f)]
  if missing:
    raise ValueError(u"Missing required field(s): {}".format(", ".join(missing)))
  result = {}
  # Number: 1..100
  try:
    number = int(row["number"])
  except Exception:
    raise ValueError(u"number must be an integer")
  if not (1 <= number <= 100):
    raise ValueError(u"number must be between 1 and 100")
  result["number"] = number
  result["title"] = normalize(row.get("title", u""))
  result["description"] = normalize(row.get("description", u""))
  result["start_date"] = parse_date(normalize(row.get("start_date", u"")), "start_date")
  if row.get("end_date"):
    end_date = parse_date(normalize(row.get("end_date", u"")), "end_date")
    if end_date < start_date:
      raise ValueError(u"end_date earlier than start_date")
    result["end_date"] = end_date
  result["responsible"] = normalize(row.get("responsible"))
  result["storage_active"] = normalize(row.get("storage_active", u""))
  result["storage_pre"] = normalize(row.get("storage_pre", u""))
  result["storage_archive"] = normalize(row.get("storage_archive", u""))
  return result

def get_obj_by_uid(uid):
  try:
    return api.get_object(uid)
  except Exception:
    return None

def _traverse_maybe(path_or_id):
  portal = ploneapi.portal.get()
  # absolute path
  if isinstance(path_or_id, string_types) and path_or_id.startswith("/"):  # CHANGED
    try:
      return portal.unrestrictedTraverse(path_or_id.lstrip("/"), default=None)
    except Exception:
      return None
  # portal-relative path or id
  try:
    return portal.unrestrictedTraverse(path_or_id, default=None)
  except Exception:
    return None

def resolve_storage(ref, required=False):
  """Resolve storage by UID, absolute/relative path, id, or title."""
  if not ref:
    if required:
      raise ValueError(u"storage reference is required")
    return u""

  # Try as UID
  obj = get_obj_by_uid(ref)
  if obj and api.get_portal_type(obj) == "StorageLocation":
    return api.get_uid(obj)

  # Try traversal by path
  obj = _traverse_maybe(ref)
  if obj and api.get_portal_type(obj) == "StorageLocation":
    return api.get_uid(obj)

  # Catalog lookup in SETUP_CATALOG by id or title
  cat = api.get_tool(SETUP_CATALOG)
  if cat:
    brains = cat(portal_type="StorageLocation", id=ref)
    if len(brains) == 1:
      return brains[0].UID
    # Title exact
    brains = cat(portal_type="StorageLocation", Title=ref)
    if len(brains) == 1:
      return brains[0].UID
    # Case-insensitive title match (fallback)
    brains = cat(portal_type="StorageLocation")
    ref_ci = ref.strip().lower()
    matches = [b for b in brains if (getattr(b, "Title", u"") or u"").strip().lower() == ref_ci]
    if len(matches) == 1:
      return matches[0].UID
    # Partial match (only if unique)
    partial = [b for b in brains if ref_ci in (getattr(b, "Title", u"") or u"").lower()]
    if len(partial) == 1:
      return partial[0].UID

  if required:
    raise ValueError(u"storage not found or ambiguous: '{}'".format(ref))
  return u""


class JournalImportAPI(BrowserView):
  """POST JSON endpoint to import Journals into a JournalRegistry."""
  def __call__(self):
    request = self.request
    if request.method != "POST":
      return self.json_response({"error": "POST required"}, status=405)
    # Disable CSRF for API usage
    alsoProvides(request, IDisableCSRFProtection)
    try:
      items = parse_payload(request.get("BODYFILE", None))
    except Exception as e:
      return self.json_response({"error": str(e)}, status=400)
    dry_run = get_bool(request.get("dry_run"))
    results = []
    created = 0
    errors = 0
    for idx, raw in enumerate(items):
      try:
        row = validate_and_normalize(raw)
        # Resolve user via "users_search" logic
        row["responsible"] = self.resolve_user(row["responsible"])
        # Resolve storages (non-UID lookups supported)
        row["storage_active"] = resolve_storage(row["storage_active"], required=True)
        row["storage_pre"] = resolve_storage(row.get("storage_pre"), required=False)
        row["storage_archive"] = resolve_storage(row.get("storage_archive"), required=False)
        if dry_run:
          results.append({"index": idx, "status": "ok", "message": u"[DRY-RUN] Valid"})
          continue
        obj = self.create_journal(row)
        created += 1
        results.append({
          "index": idx,
          "status": "ok",
          "message": u"Created: {}".format(api.get_title(obj)),
          "url": api.get_url(obj),
        })
      except Exception as e:
        errors += 1
        msg = stringify_exception(e)
        logger.error("Failed to create journal: %s", msg)  # CHANGED
        results.append({"index": idx, "status": "error", "message": msg})

    resp = {
      "processed": len(items),
      "created": created,
      "errors": errors,
      "dry_run": bool(dry_run),
      "results": results,
    }
    return self.json_response(resp, status=200 if errors == 0 else 207)

  # Responsible lookup
  def resolve_user(self, query):
    logger.info("Resolving user: %r", query)
    if not query:
      raise ValueError(u"responsible is required")

    # Exact userid
    user = ploneapi.user.get(userid=query)
    if user:
      return user.getId()

    users_view = UsersOverviewControlPanel(self.context, self.request)
    results = users_view.doSearch(query)
    results.extend(users_view.doSearch(u"*{}*".format(query)))

    # Normalize query and results to Unicode
    q = api.safe_unicode(query).lower()

    seen = set()
    items = []
    for r in results:
      uid = r.get("id")
      if not uid:
        continue
      uid_u = api.safe_unicode(uid)
      if uid_u in seen:
        continue
      seen.add(uid_u)
      fullname_u = api.safe_unicode(r.get("fullname") or u"")
      items.append({"id": uid_u, "fullname": fullname_u})

    # Sort by fullname then id (unicode)
    items.sort(key=lambda u: (u["fullname"] or u["id"]).lower())

    if not items:
      raise ValueError(u"responsible not found: '{}'".format(query))

    # Prefer exact id-insensitive match
    for it in items:
      if it["id"].lower() == q:
        return it["id"]

    if len(items) == 1:
      return items[0]["id"]

    # Fuzzy contains match (now both Unicode)
    for it in items:
      if q in it["fullname"].lower() or q in it["id"].lower():
        return it["id"]

    raise ValueError(u"responsible is ambiguous for query '{}': {}".format(
      query, u", ".join(u["id"] for u in items[:5])))

  def create_journal(self, row):
    obj = api.create(self.context, "Journal", title=row["title"])
    if row.get("description"):
      obj.setDescription(row["description"])
    setattr(obj, "number", row["number"])
    setattr(obj, "start_date", row["start_date"])
    setattr(obj, "end_date", row.get("end_date") or None)
    setattr(obj, "responsible", row["responsible"])
    setattr(obj, "storage_location_active", row.get("storage_active") or u"")
    setattr(obj, "storage_location_pre_archive", row.get("storage_pre") or u"")
    setattr(obj, "storage_location_archive", row.get("storage_archive") or u"")
    obj.reindexObject()
    return obj

  def json_response(self, data, status=200):
    res = self.request.response
    res.setHeader("Content-Type", "application/json; charset=utf-8")
    res.setStatus(status)
    # default= ensures any stray non-serializable values (e.g. exception instances) are stringified
    return json.dumps(data, ensure_ascii=False, default=json_default)

