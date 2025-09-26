# -*- coding: utf-8 -*-
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class JournalAddForm(DefaultAddForm):
    pass

class JournalAddView(DefaultAddView):
    form = JournalAddForm
    index = ViewPageTemplateFile("templates/add.pt")