# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields, Unique, sequence_ordered
from trytond.pool import PoolMeta
import logging

__all__ = ['ProductCode', 'Template', 'Product']

CODES = [('', '')]

logger = logging.getLogger(__name__)

try:
    import barcodenumber
    for code in barcodenumber.barcodes():
        CODES.append((code, code))
except ImportError:
    barcodenumber = None
    logger.error('Unable to import barcodenumber. Install barcodenumber '
        'package.')

if barcodenumber.__version__ < '0.3':
    logger.warning('Please update the barcodenumber package.')


class ProductCode(sequence_ordered(), ModelSQL, ModelView):
    'ProductCode'
    __name__ = 'product.code'
    barcode = fields.Selection(CODES, 'Code',
        help="Setting code will enable validation of the product number.")
    number = fields.Char('Number', required=True)
    product = fields.Many2One('product.product', 'Product', required=True,
        ondelete='CASCADE')
    active = fields.Boolean('Active')

    @classmethod
    def __setup__(cls):
        super(ProductCode, cls).__setup__()
        t = cls.__table__()
        cls._order.insert(0, ('product', 'ASC'))
        cls._order.insert(1, ('sequence', 'ASC'))
        cls._sql_constraints.extend([
            ('number_uniq', Unique(t, t.barcode, t.number),
             'There is another code with the same number.\n'
             'The number of the product code must be unique!')
             ])

    @staticmethod
    def default_active():
        return True

    def get_rec_name(self, name):
        if self.barcode:
            return self.barcode + self.number
        else:
            return self.number
    @classmethod
    def validate(cls, product_codes):
        super(ProductCode, cls).validate(product_codes)
        for product_code in product_codes:
            product_code.check_barcode_number()


    def check_barcode_number(self):
        'Check the code number depending of the barcode'
        if not barcodenumber:
            return True
        number = self.number

        if not self.barcode:
            return True

        if not getattr(barcodenumber, 'check_code_' +
                self.barcode.lower())(number):

            # Check if user doesn't have put barcode in number
            if number.startswith(self.barcode):
                number = number[len(self.barcode):]
                ProductCode.write([self], {
                    'number': number,
                    })
            else:
                raise UserError(gettext('product_barcode.invalid_barcode_number'
                    ))
                return False
        return True

        def decode_barcode(self):
            # Now in (barcodenumber == 0.3) there are no decoding methods
            # implemented, but in the next versions they will be.
            result = {}
            decode_method_name = 'decode_code_{}'.format(self.barcode.lower())
            if hasattr(barcodenumber, decode_method_name):
                decode_method = getattr(barcodenumber, decode_method_name)
                result = decode_method(self.number)
            return result


class Template(metaclass=PoolMeta):
    __name__ = "product.template"

    @classmethod
    def search_rec_name(cls, name, clause):
        # Get codes
        domain = super(Template, cls).search_rec_name(name, clause)
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        return [bool_op,
            domain,
            ('products.codes.number',) + tuple(clause[1:]),
            ]


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'
    codes = fields.One2Many('product.code', 'product', 'Codes')
    code_code39 = fields.Function(fields.Char('CODE 39'), 'get_code_number')
    code_ean = fields.Function(fields.Char('EAN'), 'get_code_number')
    code_ean13 = fields.Function(fields.Char('EAN 13'), 'get_code_number')
    code_ean8 = fields.Function(fields.Char('EAN 9'), 'get_code_number')
    code_gs1 = fields.Function(fields.Char('GS1'), 'get_code_number')
    code_gtin = fields.Function(fields.Char('GTIN'), 'get_code_number')
    code_isbn = fields.Function(fields.Char('ISBN'), 'get_code_number')
    code_isbn10 = fields.Function(fields.Char('ISBN 10'), 'get_code_number')
    code_isbn13 = fields.Function(fields.Char('ISBN 13'), 'get_code_number')
    code_issn = fields.Function(fields.Char('ISSN'), 'get_code_number')
    code_jan = fields.Function(fields.Char('JAN'), 'get_code_number')
    code_pzn = fields.Function(fields.Char('PZN'), 'get_code_number')
    code_upc = fields.Function(fields.Char('UPC'), 'get_code_number')
    code_upca = fields.Function(fields.Char('UPCA'), 'get_code_number')

    @classmethod
    def search_rec_name(cls, name, clause):
        # Get codes
        domain = super(Product, cls).search_rec_name(name, clause)
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        return [bool_op,
            domain,
            ('codes.number', ) + tuple(clause[1:]),
            ]

    def get_code_number(self, name):
        for code in self.codes:
            if code.barcode and code.barcode.lower() == name[5:]:
                return code.number
        return None

    @classmethod
    def copy(cls, products, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['codes'] = None
        return super(Product, cls).copy(products, default=default)
