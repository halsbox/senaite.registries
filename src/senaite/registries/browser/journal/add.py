# -*- coding: utf-8 -*-
from senaite.core.browser.dexterity.add import DefaultAddForm, DefaultAddView


class JournalAddForm(DefaultAddForm):
  portal_type = "Journal"  # explicit


class JournalAddView(DefaultAddView):
  form = JournalAddForm
