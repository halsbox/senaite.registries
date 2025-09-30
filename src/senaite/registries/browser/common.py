# -*- coding: utf-8 -*-
from plone import api as ploneapi
from six import string_types

from bika.lims import api
from senaite.core.api import dtime
from senaite.registries import messageFactory as _

_FULLNAME_REQ_CACHE_KEY = "_sr_fullname_cache"
_STORAGE_REQ_CACHE_KEY = "_sr_storage_title_cache"


def u(value):
  return api.safe_unicode(value)


def icon_url(name):
  """Return the URL of an icon name"""
  return "{}/senaite_theme/icon/{}".format(ploneapi.portal.get().absolute_url(), name)


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


def fullname_for_userid(userid, request=None):
  """Return the fullname for a userid with optional per-request cache."""
  cache = None
  uid = u(userid or u"")
  if not uid:
    return u""
  if request is not None:
    cache = getattr(request, _FULLNAME_REQ_CACHE_KEY, None)
    if cache is None:
      cache = {}
      setattr(request, _FULLNAME_REQ_CACHE_KEY, cache)
    if uid in cache:
      return cache[uid]
  user = ploneapi.user.get(userid=uid)
  fullname = (user.getProperty("fullname") or user.getUserName()) if user else uid
  fullname = api.safe_unicode(fullname)
  if request is not None and cache is not None:
    cache[uid] = fullname
  return fullname

def storage_title(uid_or_list, request=None):
  """Return the title or id of a StorageLocation by UID (or first UID in a list),
  with optional per-request cache.
  """
  cache = None
  if not uid_or_list:
    return u""
  uid = uid_or_list[0] if isinstance(uid_or_list, (list, tuple)) else uid_or_list
  key = u(uid)
  if request is not None:
    cache = getattr(request, _STORAGE_REQ_CACHE_KEY, None)
    if cache is None:
      cache = {}
      setattr(request, _STORAGE_REQ_CACHE_KEY, cache)
    if key in cache:
      return cache[key]
  try:
    target = api.get_object(uid)
  except Exception:
    title = u""
  else:
    title = u(api.get_title(target) or api.get_id(target))
  if request is not None and cache is not None:
    cache[key] = title
  return title


def stringify_exception(e):
  """Safe string representation for exceptions."""
  cls = e.__class__.__name__
  parts = []
  for a in getattr(e, "args", ()):
    try:
      parts.append(u(a))
    except Exception:
      try:
        parts.append(u(repr(a)))
      except Exception:
        parts.append(u"<unprintable>")
  return u"{}: {}".format(cls, u" ".join(parts)) if parts else u(cls)


def normalize(value, default=u""):
  """Return safe Unicode stripped string or default if value is None."""
  return u(value).strip() if value is not None else default


def json_default(obj):
  """Default serializer for json.dumps to ensure safe unicode output."""
  try:
    return u(obj)
  except Exception:
    try:
      return u(repr(obj))
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
