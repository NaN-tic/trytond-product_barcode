#This file is part product_barcode module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.

from trytond.pool import Pool
from .product import *


def register():
    Pool.register(
        ProductCode,
        Template,
        Product,
        module='product_barcode', type_='model')
