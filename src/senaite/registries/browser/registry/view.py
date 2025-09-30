# -*- coding: utf-8 -*-
import collections
from plone import api as ploneapi
from six.moves.urllib_parse import parse_qs

from bika.lims import api
from bika.lims.utils import get_link
from senaite.app.listing.view import ListingView
from senaite.registries import messageFactory as _
from senaite.registries.browser.common import (
  format_date, format_number,
  fullname_for_userid,
  icon_url, storage_title, u
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
    self.context_actions = collections.OrderedDict((
      (_("Add journal"), {
        "url": "{}/++add++Journal".format(self.context.absolute_url()),
        "permission": "senaite.registries.permissions.AddJournal",
        "icon": "{}add-journal".format(self.icon_path),
      }),
    ))
    self.default_review_state = "active"
    self.review_states = [
      {
        "id": "all", "title": _("All"),
        "contentFilter": {},
        "transitions": [],
        "columns": self.columns.keys()
      },
      {
        "id": "new", "title": _("New"),
        "contentFilter": {"review_state": "new"},
        "transitions": [],
        "columns": self.columns.keys()
      },
      {
        "id": "active", "title": _("Active"),
        "contentFilter": {"review_state": "active"},
        "transitions": [],
        "columns": self.columns.keys()
      },
      {
        "id": "pre_archive", "title": _("Pre-archive"),
        "contentFilter": {"review_state": "pre_archive"},
        "transitions": [],
        "columns": self.columns.keys()
      },
      {
        "id": "archived", "title": _("Archived"),
        "contentFilter": {"review_state": "archived"},
        "transitions": [],
        "columns": self.columns.keys()
      },
    ]


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
    item["Responsible"] = fullname_for_userid(getattr(obj, "responsible", None), self.request)
    item["StorageActive"] = storage_title(getattr(obj, "storage_location_active", None), self.request)
    item["StoragePreArchive"] = storage_title(getattr(obj, "storage_location_pre_archive", None), self.request)
    item["StorageArchive"] = storage_title(getattr(obj, "storage_location_archive", None), self.request)
    if api.security.check_permission("cmf.DeleteObjects", obj):
      item["Delete"] = (
        u'<a href="{}/delete_confirmation" title="{}">'
        u'<img src="{}" alt="{}" style="height:16px;width:16px;"/></a>'
      ).format(url, u(_("Delete")), icon_url("delete"), u(_("Delete")))
    else:
      item["Delete"] = u""

    return item
