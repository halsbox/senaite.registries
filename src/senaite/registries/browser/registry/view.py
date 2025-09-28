# -*- coding: utf-8 -*-
import collections
from plone import api as ploneapi
from senaite.app.listing.view import ListingView

from bika.lims import api
from bika.lims.utils import get_link
from senaite.registries import messageFactory as _
from senaite.registries.browser.common import (
  u,
  icon_url,
  format_number,
  format_date,
  storage_title,
  fullname_for_userid
)


class JournalRegistryView(ListingView):
  def __init__(self, context, request):
    super(JournalRegistryView, self).__init__(context, request)
    self.catalog = "portal_catalog"
    self.contentFilter = {
      "portal_type": "Journal",
      "sort_on": "modified",
      "sort_order": "descending",
      "path": {"query": api.get_path(context), "depth": 1},
    }
    self.form_id = "journal_registry_listing"
    self.title = api.get_title(context)
    self.description = api.get_description(context)
    self.icon_path = "{}/senaite_theme/icon/".format(self.portal_url)
    self.context_actions = collections.OrderedDict((
      (_("Add journal"), {
        "url": "++add++Journal",
        "permission": "cmf.AddPortalContent",
        "icon": "{}add-journal".format(self.icon_path),
      }),
    ))
    self.columns = collections.OrderedDict((
      ("Title", {"title": _("Title"), "index": "sortable_title"}),
      ("Number", {"title": _("Number"), "toggle": True}),
      ("StartDate", {"title": _("Start date"), "toggle": True}),
      ("EndDate", {"title": _("End date"), "toggle": True}),
      ("Responsible", {"title": _("Responsible"), "toggle": True}),
      ("StorageActive", {"title": _("Storage (active)"), "toggle": True}),
      ("StoragePreArchive", {"title": _("Storage (pre-archive)"), "toggle": True}),
      ("StorageArchive", {"title": _("Storage (archive)"), "toggle": True}),
      ("Delete", {"title": u"", "sortable": False}),
    ))
    self.review_states = [{
      "id": "default",
      "title": _("All"),
      "contentFilter": {},
      "transitions": [],
      "columns": self.columns.keys(),
    }]

  def folderitem(self, obj, item, index):
    obj = api.get_object(obj)
    url = api.get_url(obj)
    title = api.get_title(obj)
    desc = u(api.get_description(obj))
    title_link = u(get_link(url, value=title))
    desc_html = u"<div class='text-muted small'><em>{}</em></div>".format(desc) if desc else u""
    item["replace"]["Title"] = u"{}{}".format(title_link, desc_html)
    item["Number"] = format_number(getattr(obj, "number", None))
    item["StartDate"] = format_date(getattr(obj, "start_date", None), long_format=False, view=self)
    item["EndDate"] = format_date(getattr(obj, "end_date", None), long_format=False, view=self)
    item["Responsible"] = fullname_for_userid(getattr(obj, "responsible", None))
    item["StorageActive"] = storage_title(getattr(obj, "storage_location_active", None))
    item["StoragePreArchive"] = storage_title(getattr(obj, "storage_location_pre_archive", None))
    item["StorageArchive"] = storage_title(getattr(obj, "storage_location_archive", None))
    if api.security.check_permission("cmf.DeleteObjects", obj):
      item["Delete"] = (
        u'<a href="{}/delete_confirmation" title="{}">'
        u'<img src="{}" alt="{}" style="height:16px;width:16px;"/></a>'
      ).format(url, u(_("Delete")), icon_url("delete"), u(_("Delete")))
    else:
      item["Delete"] = u""

    return item
