# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from plone import api as ploneapi

from bika.lims import api
from senaite.registries.browser.common import (
  format_number,
  format_date,
  fullname_for_userid,
  storage_title
)


class JournalView(BrowserView):
  def formatted_number(self):
    return format_number(getattr(self.context, "number", None))

  def formatted_start_date(self):
    return format_date(getattr(self.context, "start_date", None), long_format=False, context=self.context)

  def formatted_end_date(self):
    return format_date(getattr(self.context, "end_date", None), long_format=False, context=self.context)

  def formatted_responsible(self):
    return fullname_for_userid(getattr(self.context, "responsible", None))

  def formatted_storage_location_active(self):
    return storage_title(getattr(self.context, "storage_location_active", None))

  def formatted_storage_location_pre_archive(self):
    return storage_title(getattr(self.context, "storage_location_pre_archive", None))

  def formatted_storage_location_archive(self):
    return storage_title(getattr(self.context, "storage_location_archive", None))

  def attachment(self):
    blob = getattr(self.context, "attachment", None)
    if not blob:
      return {}
    filename = getattr(blob, "filename", u"") or u"file"
    size = getattr(blob, "size", 0) or 0
    url = u"{}/@@download/attachment/{}".format(api.get_url(self.context), filename)
    return {"filename": filename, "size": size, "url": url, "size_bytes": size}
