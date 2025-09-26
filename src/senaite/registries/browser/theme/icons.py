# -*- coding: utf-8 -*-
import os

from plone.resource.interfaces import IResourceDirectory
from senaite.core.browser.globals.interfaces import IIconProvider
from senaite.core.browser.globals.interfaces import ISenaiteTheme
from zope.component import adapts, getUtility
from zope.interface import implementer

ICON_BASE_URL = "++plone++senaite.registries.static/assets/icons"


@implementer(IIconProvider)
class IconProvider(object):
  adapts(ISenaiteTheme)

  def __init__(self, view, context):
    self.view = view
    self.context = context

  def icons(self):
    """Return a mapping of icon keys -> absolute URLs.

    Keys should work with senaite_theme/icon/<key> traversal.
    Provide both 'name' and 'name.svg' for convenience.
    """
    icons = {}
    static_dir = getUtility(IResourceDirectory, name=u"++plone++senaite.registries.static")
    icon_dir = static_dir["assets"]["icons"]
    for icon in icon_dir.listDirectory():
      name, ext = os.path.splitext(icon)
      url = "{}/{}".format(ICON_BASE_URL, icon)
      icons[name] = url
      icons[icon] = url
    return icons
