# -*- coding: utf-8 -*-
from plone import api as ploneapi

from bika.lims import api
from senaite.core.api import dtime
from senaite.registries import logger
from senaite.registries import messageFactory as _


def format_number(number):
  # Translators: "№" is the number sign; keep if common in your locale.
  if number is not None:
    return _(u"№ ${number}", mapping={"number": number})
  return _(u"№ n/a")


def format_date(dt, long_format=False, view=None, context=None):
  """Return a localized date/time string for a date-like value.

  - If `view` is a ListingView (has ulocalized_time), use that (best for listings).
  - Else, if `context` is given, use @@plone.toLocalizedTime (best for object views).
  - Else, fall back to senaite.core.api.dtime.to_localized_time.

  :param dt: date/datetime/Zope DateTime or None
  :param long_format: include time if True
  :param view: a ListingView (with ulocalized_time) [optional]
  :param context: BrowserView context for @@plone [optional]
  """
  logger.info("format_date called")
  if not dt:
    logger.info("format_date: dt is None")
    return u""
  zdt = dtime.to_DT(dt)

  if view is not None and hasattr(view, "ulocalized_time"):
    logger.info("format_date: view is not None and hasattr(view, 'ulocalized_time')")
    return view.ulocalized_time(zdt, long_format=1 if long_format else 0)

  if context is not None:
    logger.info("format_date: context is not None")
    plone_tools = context.restrictedTraverse("@@plone")
    return plone_tools.toLocalizedTime(zdt, long_format=bool(long_format))

  logger.info("format_date: fallback to dtime.to_localized_time")
  return dtime.to_localized_time(zdt, long_format=bool(long_format))


def title_with_desc(obj):
  title = api.safe_unicode(api.get_title(obj))
  desc = api.safe_unicode(api.get_description(obj))
  desc_html = u"<div class='text-muted small'><em>{}</em></div>".format(desc) if desc else u""
  return u"<div>{}</div>{}".format(title, desc_html)


def fullname_for_userid(userid):
  if not userid:
    return u""
  user = ploneapi.user.get(userid=userid)
  if not user:
    return userid
  fullname = user.getProperty("fullname") or user.getUserName()
  return api.safe_unicode(fullname)


def storage_title(uid_or_list):
  logger.info("storage_title called")
  if not uid_or_list:
    logger.info("storage_title: uid_or_list is None")
    return u""
  uid = uid_or_list[0] if isinstance(uid_or_list, (list, tuple)) else uid_or_list
  try:
    target = api.get_object(uid)
    logger.info("storage_title: target is not None")
    return api.safe_unicode(api.get_title(target) or api.get_id(target))
  except Exception:
    logger.info("storage_title: Exception")
    return u""

def stringify_exception(e):
  # Do NOT call unicode(e) directly; build from args safely
  cls = e.__class__.__name__
  parts = []
  for a in getattr(e, "args", ()):
    try:
      parts.append(api.safe_unicode(a))
    except Exception:
      try:
        parts.append(api.safe_unicode(repr(a)))
      except Exception:
        parts.append(u"<unprintable>")
  return u"{}: {}".format(cls, u" ".join(parts)) if parts else api.safe_unicode(cls)

def normalize(value, default=u""):
  return api.safe_unicode(value).strip() if value is not None else default

def json_default(obj):
  # Best-effort Unicode conversion; final fallback to repr
  try:
    return api.safe_unicode(obj)
  except Exception:
    try:
      return api.safe_unicode(repr(obj))
    except Exception:
      return u"<unserializable>"

def get_bool(val):
  if isinstance(val, bool):
    return val
  if isinstance(val, string_types):  # CHANGED
    return val.strip().lower() in ("1", "true", "yes", "y", "on")
  return False