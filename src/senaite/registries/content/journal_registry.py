# -*- coding: utf-8 -*-
from plone.supermodel import model
from senaite.core.content.base import Container
from senaite.registries.interfaces import IJournalRegistry
from zope.interface import implementer

class IJournalRegistrySchema(model.Schema):
    """Schema for a JournalRegistry."""

@implementer(IJournalRegistry, IJournalRegistrySchema)
class JournalRegistry(Container):
    """Container for Journal records."""