# -*- coding: utf-8 -*-
from zope.interface import implements

from bika.lims.interfaces import IGuardAdapter


class JournalGuardAdapter(object):
  implements(IGuardAdapter)

  def __init__(self, context):
    self.context = context

  def guard(self, action):
    method = getattr(self, "guard_{}".format(action), None)
    return method() if method else True

  def guard_start_using(self):
    # new -> active
    return bool(getattr(self.context, "responsible", None)
                and getattr(self.context, "storage_location_active", u""))

  def guard_end_using(self):
    # active -> pre_archive
    # Pre-archive storage or end_date must be provided; end_date will be auto-set if missing
    return bool(getattr(self.context, "storage_location_pre_archive", u"") or
                getattr(self.context, "end_date", None))

  def guard_resume_using(self):
    # pre_archive -> active (allow moving back only if active storage present)
    return bool(getattr(self.context, "storage_location_active", u""))

  def guard_archive(self):
    # pre_archive -> archived requires archive storage
    return bool(getattr(self.context, "storage_location_archive", u""))

  def guard_unarchive(self):
    # archived -> pre_archive (always allowed)
    return True
