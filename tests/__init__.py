# This file is part product_barcode module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.product_barcode.tests.test_product_barcode import suite
except ImportError:
    from .test_product_barcode import suite

__all__ = ['suite']
