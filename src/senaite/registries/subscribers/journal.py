# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from zope.component import adapter

from bika.lims import api


@adapter(IAfterTransitionEvent)
def on_journal_transition(event):
  obj = event.object
  if api.get_portal_type(obj) != "Journal":
    return

  tid = event.transition and event.transition.id or ""
  today_midnight = DateTime().earliestTime()

  if tid == "start_using":
    if not getattr(obj, "start_date", None):
      setattr(obj, "start_date", today_midnight)
      obj.reindexObject(idxs=["start_date"])
  elif tid == "end_using":
    if not getattr(obj, "end_date", None):
      setattr(obj, "end_date", today_midnight)
      obj.reindexObject(idxs=["end_date"])
