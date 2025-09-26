# -*- coding: utf-8 -*-
from plone.supermodel import model
from zope.interface import implementer

from senaite.core.content.base import Container
from senaite.registries.interfaces import IJournalRegistry


class IJournalRegistrySchema(model.Schema):
  """Schema for a JournalRegistry."""


@implementer(IJournalRegistry, IJournalRegistrySchema)
class JournalRegistry(Container):
  """Container for Journal records."""
