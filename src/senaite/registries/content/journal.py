# -*- coding: utf-8 -*-
from plone import api as ploneapi
from plone.autoform import directives
from senaite.registries import messageFactory as _
from plone.supermodel import model
from zope import schema
from zope.interface import implementer

from bika.lims.catalog import SETUP_CATALOG
from senaite.core.content.base import Item
from senaite.core.schema import DatetimeField
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.datetimewidget import DatetimeWidget
from senaite.core.z3cform.widgets.number import IntFieldWidget as NumberWidgetFactory
from senaite.core.z3cform.widgets.queryselect import QuerySelectWidgetFactory
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from senaite.registries.interfaces import IJournal


class IJournalSchema(model.Schema):
  directives.order_after(number="title")
  directives.widget("number", NumberWidgetFactory)
  number = schema.Int(
    title=_(u"Number"),
    description=_(u"Journal number between 1 and 100"),
    required=True,
    min=1, max=100,
  )

  directives.order_after(start_date="number")
  directives.widget("start_date", DatetimeWidget, show_time=False)
  start_date = DatetimeField(
    title=_(u"Start Date"),
    required=True,
  )

  directives.order_after(end_date="start_date")
  directives.widget("end_date", DatetimeWidget, show_time=False)
  end_date = DatetimeField(
    title=u"End Date",
    required=False,
  )

  directives.order_after(responsible="end_date")
  directives.widget(
    "responsible",
    QuerySelectWidgetFactory,
    api_url="@@users_search",
    display_template="${fullname}",
    search_index="q",
    value_key="id",
    value_query_index="id",
    search_wildcard=False,
    allow_user_value=False,
    multi_valued=False,
    columns=[
      {"name": "fullname", "label": u"Name", "width": "70", "align": "left"},
      {"name": "id", "label": u"User ID", "width": "30", "align": "left"},
    ],
    limit=10,
  )
  responsible = schema.TextLine(
    title=u"Responsible user",
    description=u"User responsible for maintaining the journal",
    required=True,
  )

  directives.order_after(storage_location_active="responsible")
  directives.widget(
    "storage_location_active",
    UIDReferenceWidgetFactory,
    catalog=SETUP_CATALOG,
    query={"is_active": True, "sort_on": "sortable_title", "sort_order": "ascending"},
  )
  storage_location_active = UIDReferenceField(
    title=u"Storage location in use",
    description=u"Select the storage location of the journal while in active use",
    required=True,
    multi_valued=False,
    allowed_types=("StorageLocation",),
  )

  directives.order_after(storage_location_pre_archive="storage_location_active")
  directives.widget(
    "storage_location_pre_archive",
    factory=UIDReferenceWidgetFactory,
    catalog=SETUP_CATALOG,
    query={"is_active": True, "sort_on": "sortable_title", "sort_order": "ascending"},
  )
  storage_location_pre_archive = UIDReferenceField(
    title=u"Storage location (before archiving)",
    description=u"Storage location before moving the journal to archive",
    required=False,
    multi_valued=False,
    allowed_types=("StorageLocation",),
  )

  directives.order_after(storage_location_archive="storage_location_pre_archive")
  directives.widget(
    "storage_location_archive",
    factory=UIDReferenceWidgetFactory,
    catalog=SETUP_CATALOG,
    query={"is_active": True, "sort_on": "sortable_title", "sort_order": "ascending"},
  )
  storage_location_archive = UIDReferenceField(
    title=u"Storage location (archive)",
    description=u"Storage location after moving the journal to archive",
    required=False,
    multi_valued=False,
    allowed_types=("StorageLocation",),
  )


@implementer(IJournal, IJournalSchema)
class Journal(Item):
  def get_widget_responsible_records(self, name, widget, field, context, default):
    """Provide render data for the stored userid (single-valued)."""
    userid = getattr(self, "responsible", None)
    if not userid:
      return default

    user = ploneapi.user.get(userid=userid)
    fullname = user.getProperty("fullname") if user else userid
    return {
      userid: {
        "id": userid,
        "fullname": fullname,
        "Description": "",
        "review_state": "active",
      }
    }
