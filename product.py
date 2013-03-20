#This file is part product_barcode module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta

__all__ = ['ProductCode', 'Product']
__metaclass__ = PoolMeta

HAS_BARCODENUMBER = False
CODES = [('', '')]
try:
    import barcodenumber
    HAS_BARCODENUMBER = True
    for code in barcodenumber.barcodes():
        CODES.append((code, code))
except ImportError:
    logging.getLogger('product barcode').warning(
            'Unable to import barcodenumber. Product code number validation disabled.')

class ProductCode(ModelSQL, ModelView):
    'ProductCode'
    __name__ = 'product.code'
    barcode = fields.Selection(CODES, 'Code', 
        help="Setting code will enable validation of the product number.")
    number = fields.Char('Number', required=True)
    product = fields.Many2One('product.product', 'Product', required=True)

    @classmethod
    def __setup__(cls):
        super(ProductCode, cls).__setup__()
        cls._constraints += [
            ('check_barcode_number', 'invalid_barcode_number'),
        ]
        cls._error_messages.update({
            'invalid_barcode_number': 'Invalid Barcode number!',
        })

    def get_rec_name(self, name):
        if self.barcode:
            return self.barcode + self.number
        else:
            return self.number

    def check_barcode_number(self):
        '''
        Check the code number depending of the barcode.
        '''
        if not HAS_BARCODENUMBER:
            return True
        number = self.number

        if not self.barcode:
            return True

        if not getattr(barcodenumber, 'check_code_' +
                self.barcode.lower())(number):

            #Check if user doesn't have put barcode in number
            if number.startswith(self.barcode):
                number = vat_number[len(self.barcode):]
                ProductCode.write([self], {
                    'number': number,
                    })
            else:
                return False
        return True


class Product:
    'Product'
    __name__ = 'product.product'
    codes = fields.One2Many('product.code', 'product', 'Codes')

    @classmethod
    def search_rec_name(cls, name, clause):
        number = clause[2:][0][1:][:-1]
        # Get codes
        codes = Pool().get('product.code').search([
                    ('number', '=', number),
                    ], order=[])
        products = [code.product for code in codes]

        #Get products by code
        prod_codes = Pool().get('product.product').search([
                    ('code', '=', number),
                    ], order=[])

        products = products + prod_codes
        if products:
            return [('id', 'in', [product.id for product in products])]
        return super(Product, cls).search_rec_name(name, clause)
