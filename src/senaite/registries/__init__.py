# -*- coding: utf-8 -*-
import logging

from senaite.registries.config import PRODUCT_NAME
from bika.lims.api import get_request
from senaite.registries.interfaces import ISenaiteRegistriesLayer
from zope.i18nmessageid import MessageFactory

messageFactory = MessageFactory(PRODUCT_NAME)
logger = logging.getLogger(PRODUCT_NAME)

def is_installed():
    """Whether senaite.registries is installed (browser layer registered)."""
    req = get_request()
    return ISenaiteRegistriesLayer.providedBy(req)

def check_installed(default_return):
    """Decorator to block functions if product is not installed."""
    def decorator(func):
        def wrapped(*args, **kwargs):
            if not is_installed():
                return default_return
            return func(*args, **kwargs)
        return wrapped
    return decorator

def initialize(context):
    """Initializer for Zope2 product (not much to do as all is Dexterity)."""
    logger.info("*** Initializing SENAITE.REGISTRIES ***")