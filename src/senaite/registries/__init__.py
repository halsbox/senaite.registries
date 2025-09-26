# -*- coding: utf-8 -*-
import logging
from zope.i18nmessageid import MessageFactory

from bika.lims.api import get_request
from senaite.registries.config import PRODUCT_NAME
from senaite.registries.interfaces import ISenaiteRegistriesLayer

messageFactory = MessageFactory(PRODUCT_NAME)
logger = logging.getLogger(PRODUCT_NAME)


def is_installed():
  req = get_request()
  return ISenaiteRegistriesLayer.providedBy(req)


def check_installed(default_return):
  def decorator(func):
    def wrapped(*args, **kwargs):
      if not is_installed():
        return default_return
      return func(*args, **kwargs)
    return wrapped
  return decorator


def initialize(context):
  logger.info("*** Initializing SENAITE.REGISTRIES ***")
