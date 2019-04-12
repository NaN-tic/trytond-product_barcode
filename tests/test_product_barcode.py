# This file is part of the product_barcode module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
from decimal import Decimal
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool


class ProductBarcodeTestCase(ModuleTestCase):
    'Test Product Barcode module'
    module = 'product_barcode'

    @with_transaction()
    def test_barcode(self):
        'Test product barcode'
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        ProductCode = pool.get('product.code')

        unit, = Uom.search([
                ('name', '=', 'Unit'),
                ], limit=1)

        pt1, = Template.create([{
                'name': 'P1',
                'type': 'goods',
                'list_price': Decimal(20),
                'default_uom': unit.id,
                'products': [('create', [{
                                'code': '1',
                                }])]
                }])
        product, = pt1.products

        code, = ProductCode.create([{
                'product': product,
                'barcode': 'EAN13',
                'number': '9788478290222',
                }])
        self.assertEqual(code.number, '9788478290222')
        self.assertEqual(code.barcode, 'EAN13')
        self.assertEqual(product.code_ean13, '9788478290222')


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        ProductBarcodeTestCase))
    return suite
