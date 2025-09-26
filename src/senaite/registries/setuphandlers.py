# -*- coding: utf-8 -*-
from plone import api as ploneapi
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation

from bika.lims import api
from senaite.registries import logger
from senaite.registries.config import PROFILE_ID, PRODUCT_NAME

JOURNALS_ID = "journals"
REGISTRIES_FOLDER_ID = "senaite_registries"  # or "registries" if you prefer
SITE_STRUCTURE = [
  # Tuples of (portal_type, obj_id, obj_title, parent_path, display_type)
  # If parent_path is None, assume folder_id is portal
  ("RegistriesRootFolder", "senaite_registries", "Registries", None, True),
  ("JournalRegistry", "journals", "Journals", "senaite_registries", True)
]


def post_install(portal_setup):
  logger.info("{} install handler [BEGIN]".format(PRODUCT_NAME.upper()))
  context = portal_setup._getImportContext(PROFILE_ID)
  portal = context.getSite()  # noqa

  # (re)create structure and ensure nav visibility
  setup_site_structure(portal)

  # IMPORTANT: recatalog existing objects that were hard-uncataloged on uninstall
  reindex_registries_structure(portal)

  logger.info("{} install handler [DONE]".format(PRODUCT_NAME.upper()))


def setup_site_structure(portal):
  logger.info("Setup site structure ...")

  def resolve_parent(parent_path):
    if not parent_path:
      return portal
    # path relative to portal
    return portal.unrestrictedTraverse(parent_path.lstrip("/"), default=None)

  for portal_type, obj_id, obj_title, parent_path, display in SITE_STRUCTURE:
    parent = resolve_parent(parent_path)
    if not parent:
      logger.warn("Parent path {} does not exist".format(parent_path))
      continue

    if obj_id in parent:
      logger.info("Object {}/{} already exists"
                  .format(api.get_path(parent), obj_id))
      obj = parent._getOb(obj_id)
    else:
      logger.info("Creating {} {}/{}".format(
        portal_type, api.get_path(parent), obj_id))
      obj = api.create(parent, portal_type, id=obj_id, title=obj_title)

    if display:
      display_in_nav(obj)

  logger.info("Setup site structure [DONE]")


def display_in_nav(obj):
  # ensure the type is shown in nav
  registry_id = "plone.displayed_types"
  portal_type = api.get_portal_type(obj)
  to_display = ploneapi.portal.get_registry_record(registry_id, default=())
  if portal_type not in to_display:
    ploneapi.portal.set_registry_record(registry_id, to_display + (portal_type,))

  # ensure the object is not excluded from nav
  nav_exclude = IExcludeFromNavigation(obj, None)
  if nav_exclude:
    nav_exclude.exclude_from_nav = False
    obj.reindexObject(idxs=["exclude_from_nav"])


def reindex_registries_structure(portal):
  """Recatalog the registries subtree so the sidebar/menu can see it again."""
  logger.info("*** Reindex registries structure ***")
  root = getattr(portal, "senaite_registries", None)
  if not root:
    logger.info("No 'senaite_registries' container found [SKIP]")
    return

  def reindex(obj, recurse=False):
    if api.is_object(obj):
      try:
        logger.info("Reindexing %r", obj)
        obj.reindexObject()
      except Exception as e:
        logger.warn("Reindex failed for %r: %s", obj, e)
    if recurse:
      ov = getattr(obj, "objectValues", None)
      if callable(ov):
        for child in ov():
          reindex(child, recurse=True)

  # children first, then root
  ov = getattr(root, "objectValues", None)
  if callable(ov):
    for child in ov():
      reindex(child, recurse=True)
  reindex(root, recurse=False)


def pre_install(portal_setup):
  pass


def post_uninstall(portal_setup):
  logger.info("SENAITE.REGISTRIES uninstall handler [BEGIN]")
  portal = portal_setup._getImportContext(
    "profile-senaite.registries:uninstall").getSite()

  # Hard-uncatalog (by path) from core catalogs
  hard_uncatalog_registries_structure(portal)

  # Remove our types from Plone’s displayed types
  cleanup_displayed_types()

  # Optional: hide the root (if still present)
  hide_registries_root(portal)

  logger.info("SENAITE.REGISTRIES uninstall handler [DONE]")


def hard_uncatalog_registries_structure(portal):
  """Uncatalog by path from ZCatalogs (FTIs not required)."""
  logger.info("*** Hard-uncatalog registries structure ***")

  registries = getattr(portal, "senaite_registries", None)
  if not registries:
    logger.info("No 'senaite_registries' container found [SKIP]")
    return

  catalog_ids = ("portal_catalog", "uid_catalog")

  def catalogs():
    for cid in catalog_ids:
      cat = api.get_tool(cid)
      if cat:
        yield cid, cat

  def uncatalog_path(path):
    for cid, cat in catalogs():
      try:
        cat.uncatalog_object(path)
        logger.info("Uncataloged from %s: %s", cid, path)
      except Exception as e:
        logger.warn("Uncatalog failed in %s for %s: %s", cid, path, e)

  def walk(obj):
    ov = getattr(obj, "objectValues", None)
    if callable(ov):
      for child in list(ov()):
        walk(child)
    path = "/".join(obj.getPhysicalPath())
    uncatalog_path(path)

  walk(registries)


def cleanup_displayed_types():
  reg_id = "plone.displayed_types"
  current = tuple(ploneapi.portal.get_registry_record(reg_id, default=()))
  if not current:
    return
  remove = {"RegistriesRootFolder", "JournalRegistry", "Journal"}
  new = tuple(t for t in current if t not in remove)
  if new != current:
    ploneapi.portal.set_registry_record(reg_id, new)


def hide_registries_root(portal):
  root = getattr(portal, "senaite_registries", None)
  if not root:
    return
  try:
    from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
    nav = IExcludeFromNavigation(root, None)
    if nav:
      nav.exclude_from_nav = True
      root.reindexObject(idxs=["exclude_from_nav"])
  except Exception:
    # Fallback if behavior not present
    if hasattr(root, "exclude_from_nav"):
      setattr(root, "exclude_from_nav", True)
      try:
        root.reindexObject(idxs=["exclude_from_nav"])
      except Exception:
        pass
