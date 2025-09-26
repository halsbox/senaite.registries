# -*- coding: utf-8 -*-
import json
from Products.Five.browser import BrowserView
from six.moves.urllib_parse import urlencode
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound

from senaite.core.browser.usergroup.usergroups_usersoverview import UsersOverviewControlPanel
from senaite.registries import logger


@implementer(IPublishTraverse)
class UsersSearch(BrowserView):
  def publishTraverse(self, request, name):
    if not hasattr(self, "_subpath"):
      self._subpath = []
    self._subpath.append(name)
    return self

  def __call__(self):
    sub = getattr(self, "_subpath", [])
    if sub and sub[0] != "search":
      raise NotFound(self, "/".join(sub), self.request)
    query = self.request.get("q") or ""
    query = query.strip()
    try:
      start = int(self.request.get("b_start", 0));
      start = max(start, 0)
    except Exception:
      start = 0
    try:
      limit = int(self.request.get("limit", 30));
      limit = max(limit, 1)
    except Exception:
      limit = 30
    users_view = UsersOverviewControlPanel(self.context, self.request)
    results = users_view.doSearch(query)
    # Some PAS plugins (e.g. ldap) do need wildcard
    results.extend(users_view.doSearch("*{0}*".format(query)))
    seen = set()
    items = []
    for r in results:
      if r.get("id") in seen:
        continue
      seen.add(r.get("id"))
      items.append({"id": r.get("id"), "fullname": r.get("fullname")})
    items.sort(key=lambda user: (user["fullname"] or "").lower())
    count = len(items)
    page = start // limit + 1
    pages = max(1, -(-count // limit))
    logger.debug(
      "Found %s users for query '%s', returning page %s of %s",
      count, query, page, pages
    )
    self.request.response.setHeader("Content-Type", "application/json")
    return json.dumps({
      "items": items[start:start + limit],
      "count": count,
      "page": page,
      "pages": pages,
      "next": self.page_url(page + 1, limit) if page < pages else "",
      "previous": self.page_url(page - 1, limit) if page > 1 else ""
    })

  def page_url(self, page, limit):
    params = []
    for key in ("catalog", "limit", "column_names", "field_name", "q"):
      val = self.request.get(key)
      if val:
        if isinstance(val, (list, tuple)):
          for sub_val in val:
            params.append((key, sub_val))
        else:
          params.append((key, val))
    params.append(("b_start", str((page - 1) * limit)))
    return "{0}?{1}".format(self.request.get("PATH_INFO"), urlencode(params))
