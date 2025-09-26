# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.browser.edit import DefaultEditForm


class JournalEditForm(DefaultEditForm):
  index = ViewPageTemplateFile("templates/edit.pt")
