# -*- coding: utf-8 -*-
from plone import api as ploneapi
from six import string_types

from bika.lims import api
from senaite.core.api import dtime
from senaite.registries import messageFactory as _


def format_number(number):
  """Return localized '№ <number>' or '№ n/a'."""
  if number is not None:
    return _(u"№ ${number}", mapping={"number": number})
  return _(u"№ n/a")


def format_date(dt, long_format=False, view=None, context=None):
  """Return a localized date/time string for a date-like value.

  - If `view` has ulocalized_time, use it (best for listings).
  - Else, if `context` is given, use @@plone.toLocalizedTime.
  - Else, fallback to senaite.core.api.dtime.to_localized_time.
  """
  if not dt:
    return u""
  zdt = dtime.to_DT(dt)

  if view is not None and hasattr(view, "ulocalized_time"):
    return view.ulocalized_time(zdt, long_format=1 if long_format else 0)

  if context is not None:
    plone_tools = context.restrictedTraverse("@@plone")
    return plone_tools.toLocalizedTime(zdt, long_format=bool(long_format))

  return dtime.to_localized_time(zdt, long_format=bool(long_format))


def title_with_desc(obj):
  """HTML title with optional description (used in listings)."""
  title = api.safe_unicode(api.get_title(obj))
  desc = api.safe_unicode(api.get_description(obj))
  desc_html = u"<div class='text-muted small'><em>{}</em></div>".format(desc) if desc else u""
  return u"<div>{}</div>{}".format(title, desc_html)


def fullname_for_userid(userid):
  if not userid:
    return u""
  user = ploneapi.user.get(userid=userid)
  if not user:
    return api.safe_unicode(userid)
  fullname = user.getProperty("fullname") or user.getUserName()
  return api.safe_unicode(fullname)


def storage_title(uid_or_list):
  """Return the title or id of a StorageLocation by UID (or first UID in a list)."""
  if not uid_or_list:
    return u""
  uid = uid_or_list[0] if isinstance(uid_or_list, (list, tuple)) else uid_or_list
  try:
    target = api.get_object(uid)
  except Exception:
    return u""
  return api.safe_unicode(api.get_title(target) or api.get_id(target))


def stringify_exception(e):
  """Safe string representation for exceptions."""
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
  """Return safe Unicode stripped string or default if value is None."""
  return api.safe_unicode(value).strip() if value is not None else default


def json_default(obj):
  """Default serializer for json.dumps to ensure safe unicode output."""
  try:
    return api.safe_unicode(obj)
  except Exception:
    try:
      return api.safe_unicode(repr(obj))
    except Exception:
      return u"<unserializable>"


def get_bool(val):
  """Convert common truthy/falsey values to bool."""
  if isinstance(val, bool):
    return val
  if isinstance(val, (int, long)):  # noqa: F821 for Python 2
    return val != 0
  if isinstance(val, string_types):
    return val.strip().lower() in ("1", "true", "yes", "y", "on")
  return False
