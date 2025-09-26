# -*- coding: utf-8 -*-
from plone.supermodel import model
from senaite.core.content.base import Container
from senaite.core.interfaces import IHideActionsMenu
from senaite.registries.interfaces import IRegistriesRootFolder
from zope.interface import implementer

class IRegistriesRootFolderSchema(model.Schema):
    """Schema for RegistriesRootFolder (no fields required)."""

@implementer(IRegistriesRootFolder, IRegistriesRootFolderSchema, IHideActionsMenu)
class RegistriesRootFolder(Container):
    """Top-level folder for all registries."""