# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView


class JournalAddForm(DefaultAddForm):
  pass


class JournalAddView(DefaultAddView):
  form = JournalAddForm
  index = ViewPageTemplateFile("templates/add.pt")
