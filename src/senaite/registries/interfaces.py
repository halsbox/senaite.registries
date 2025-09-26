# -*- coding: utf-8 -*-
from senaite.lims.interfaces import ISenaiteLIMS
from zope.interface import Interface

from senaite.core.interfaces import ISenaiteFormLayer


class ISenaiteRegistriesLayer(ISenaiteLIMS, ISenaiteFormLayer):
  """Browser Layer for senaite.registries"""


class IRegistriesRootFolder(Interface):
  """Marker interface for RegistriesRootFolder."""


class IJournalRegistry(Interface):
  """Marker interface for JournalRegistry."""


class IJournal(Interface):
  """Marker interface for Journal objects."""
