# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from plone import api as ploneapi

from bika.lims import api
from senaite.registries.browser.common import icon_url, u

class RegistriesRootView(BrowserView):
  """Landing page for the Registries root folder.
  Renders tiles with icon + caption linking to each Registry inside.
  """

  ICONS = {
    "JournalRegistry": "journal-registry",
  }
  DEFAULT_ICON = "registries"

  def registries(self):
    """Return a list of registries."""
    items = []
    ov = getattr(self.context, "objectValues", None)
    if not callable(ov):
      return items

    for child in ov():
      # Ensure user can see it
      if not ploneapi.user.has_permission("View", obj=child):
        continue
      pt = api.get_portal_type(child)
      if not pt or not pt.lower().endswith("registry"):
        continue
      icon_name = self.ICONS.get(pt, self.DEFAULT_ICON)
      items.append({
        "id": api.get_id(child),
        "portal_type": pt,
        "url": api.get_url(child),
        "icon": icon_url(icon_name),
      })
    items.sort(key=lambda x: (x["title"] or "").lower())
    return items
