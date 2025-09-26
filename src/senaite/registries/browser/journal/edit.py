# -*- coding: utf-8 -*-
from plone.dexterity.browser.edit import DefaultEditForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class JournalEditForm(DefaultEditForm):
    index = ViewPageTemplateFile("templates/edit.pt")