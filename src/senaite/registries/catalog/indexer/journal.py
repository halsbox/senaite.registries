# -*- coding: utf-8 -*-
from plone.indexer import indexer

from senaite.registries.interfaces import IJournal


@indexer(IJournal)
def responsible(instance):
  """Index the 'responsible' userid for filtering."""
  return getattr(instance, "responsible", None) or u""
