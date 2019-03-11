from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from odoo import fields


class HubSaleOrderImportMapper(Component):
    _name = 'hub.sale.order.import.mapper'
    _inherit = 'hub.import.mapper'
    _apply_on = 'hub.sale.order'

    direct = [
        ('name', 'name'),
        ('track_id', 'track_id'),
        ('order_status', 'order_status'),
        ('payment_status', 'payment_status'),
        ('store_id', 'store_id'),
        ('group_id', 'group_id'),
        ('total_amount', 'total_amount'),
        ('total_discount', 'total_discount'),
        ('total_output_vat', 'total_tax'),
        ('total_service_fee', 'total_service_fee'),
        ('total_insurance_amount', 'total_insurance_amount'),
        ('total_vendor_cost', 'total_vendor_cost'),
        ('total_supplier_cost', 'total_supplier_cost'),
    ]
    children = [
        ('line_items', 'hub_line_ids', 'hub.sale.order.line')]

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def currency_id(self, record):
        if 'currency' in record:
            currency = record.get('currency')
            return {'currency_id': self.env.ref(f'base.{currency}').id}
        return {}

    @mapping
    def created_at(self, record):
        if 'created_at' in record:
            return {
                'created_at': fields.Datetime.from_string(
                    record['created_at'])}
        return {}

    @mapping
    def updated_at(self, record):
        if 'updated_at' in record:
            return {
                'updated_at': fields.Datetime.from_string(
                    record['updated_at'])}
        return {}

    @mapping
    def vendor_currency_id(self, record):
        if 'vendor_currency' in record:
            currency = record.get('vendor_currency')
            return {'vendor_currency_id': self.env.ref(f'base.{currency}').id}
        return {}

    @mapping
    def supplier_currency_id(self, record):
        if 'supplier_currency' in record:
            currency = record.get('supplier_currency')
            return {
                'supplier_currency_id': self.env.ref(f'base.{currency}').id}
        return {}


class HubSaleOrderLineImportMapper(Component):

    _name = 'hub.sale.order.line.import.mapper'
    _inherit = 'hub.import.mapper'
    _apply_on = 'hub.sale.order.line'

    direct = [
        ('product_type', 'line_type'),
        ('product_category', 'line_category'),
        ('sequence', 'sequence'),
        ('product_id', 'name'),
        ('line_status', 'state'),
        ('is_domestic_ksa', 'is_domestic_ksa'),
    ]

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def created_at(self, record):
        if 'created_at' in record:
            return {
                'created_at': fields.Datetime.from_string(
                    record['created_at'])}
        return {}

    @mapping
    def updated_at(self, record):
        if 'updated_at' in record:
            return {
                'updated_at': fields.Datetime.from_string(
                    record['updated_at'])}
        return {}

    @mapping
    def vendor_name(self, record):
        if 'vendor' in record:
            return {'vendor_name': record['vendor'].get('name')}
        return {}

    @mapping
    def vendor_confirmation_number(self, record):
        if 'vendor' in record:
            return {'vendor_confirmation_number': record['vendor'].get(
                'confirmation_number')}
        return {}

    @mapping
    def vendor_currency_id(self, record):
        if 'price' not in record:
            return {}
        if 'cost' not in record['price']:
            return {}
        if 'vendor' not in record['price']['cost']:
            return {}
        vendor = record['price']['cost'].get('vendor')
        currency = vendor.get('currency')
        return {'vendor_currency_id': self.env.ref(f'base.{currency}').id}

    @mapping
    def vendor_cost_amount(self, record):
        if 'price' not in record:
            return {}
        if 'cost' not in record['price']:
            return {}
        if 'vendor' not in record['price']['cost']:
            return {}
        vendor = record['price']['cost'].get('vendor')
        cost = vendor.get('untaxed_amount', 0.0) + \
            vendor.get('input_vat_amount', 0.0)
        return {'vendor_cost_amount': cost}

    @mapping
    def supplier_name(self, record):
        if 'supplier' in record:
            return {'supplier_name': record['supplier'].get('name')}
        return {}

    @mapping
    def supplier_confirmation_number(self, record):
        if 'supplier' in record:
            return {'supplier_confirmation_number': record['supplier'].get(
                'confirmation_number')}
        return {}

    @mapping
    def supplier_currency_id(self, record):
        if 'price' not in record:
            return {}
        if 'cost' not in record['price']:
            return {}
        if 'supplier' not in record['price']['cost']:
            return {}
        supplier = record['price']['cost'].get('supplier')
        currency = supplier.get('currency')
        return {'supplier_currency_id': self.env.ref(f'base.{currency}').id}

    @mapping
    def supplier_cost_amount(self, record):
        if 'price' not in record:
            return {}
        if 'cost' not in record['price']:
            return {}
        if 'supplier' not in record['price']['cost']:
            return {}
        supplier = record['price']['cost'].get('supplier')
        cost = supplier.get('untaxed_amount', 0.0) + \
            supplier.get('input_vat_amount', 0.0)
        return {'supplier_cost_amount': cost}

    @mapping
    def exchange_rate(self, record):
        if 'price' not in record:
            return {}
        if 'cost' not in record['price']:
            return {}
        return {
            'exchange_rate': record['price']['cost'].get(
                'supplier_vendor_rate')}

    @mapping
    def traveller(self, record):
        if record.get('product_type').lower() != 'flight':
            return {}
        if 'traveller' not in record:
            return {}
        return {'traveller': record['traveller'].get('name')}

    @mapping
    def traveller_type(self, record):
        if record.get('product_type').lower() != 'flight':
            return {}
        if 'traveller' not in record:
            return {}
        return {'traveller_type': record['traveller'].get('type')}

    @mapping
    def ticket_number(self, record):
        if record.get('product_type').lower() != 'flight':
            return {}
        if 'traveller' not in record:
            return {}
        return {'ticket_number': record['traveller'].get('ticket_number')}

    @mapping
    def office_id(self, record):
        if record.get('product_type').lower() != 'flight':
            return {}
        if 'office' not in record:
            return {}
        return {'office_id': record['office'].get('office_id')}

    @mapping
    def ticketing_office_id(self, record):
        if record.get('product_type').lower() != 'flight':
            return {}
        if 'office' not in record:
            return {}
        return {
            'ticketing_office_id': record['office'].get('ticketing_office_id')
        }

    @mapping
    def tour_code_office_id(self, record):
        if record.get('product_type').lower() != 'flight':
            return {}
        if 'office' not in record:
            return {}
        return {
            'tour_code_office_id': record['office'].get('tour_code_office_id')
        }

    @mapping
    def contract(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'hotel' not in record:
            return {}
        return {'contract': record['hotel'].get('contract')}

    @mapping
    def hotel_id(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'hotel' not in record:
            return {}
        return {'hotel_id': record['hotel'].get('hotel_id')}

    @mapping
    def hotel_country(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'hotel' not in record:
            return {}
        return {'hotel_country': record['hotel'].get('country')}

    @mapping
    def hotel_city(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'hotel' not in record:
            return {}
        return {'hotel_city': record['hotel'].get('city')}

    @mapping
    def currency_id(self, record):
        if 'price' not in record:
            return {}
        if 'sale' not in record['price']:
            return {}
        currency = record['price']['sale'].get('currency')
        return {'currency_id': self.env.ref(f'base.{currency}').id}

    @mapping
    def sale_price(self, record):
        if 'price' not in record:
            return {}
        if 'sale' not in record['price']:
            return {}
        return {'sale_price': record['price']['sale'].get('untaxed_amount')}

    @mapping
    def service_fee_amount(self, record):
        if 'price' not in record:
            return {}
        if 'sale' not in record['price']:
            return {}
        return {
            'service_fee_amount': record['price']['sale'].get('service_fee')
        }

    @mapping
    def discount_amount(self, record):
        if 'price' not in record:
            return {}
        if 'sale' not in record['price']:
            return {}
        return {'discount_amount': record['price']['sale'].get('discount')}

    @mapping
    def tax_amount(self, record):
        if 'price' not in record:
            return {}
        if 'sale' not in record['price']:
            return {}
        return {'tax_amount': record['price']['sale'].get('output_vat')}

    @mapping
    def subtotal_amount(self, record):
        if 'price' not in record:
            return {}
        if 'sale' not in record['price']:
            return {}
        return {'total_amount': record['price']['sale'].get('subtotal_amount')}

    @mapping
    def total_amount(self, record):
        if 'price' not in record:
            return {}
        if 'sale' not in record['price']:
            return {}
        return {'total_amount': record['price']['sale'].get('total_amount')}

    @mapping
    def tax_code(self, record):
        if 'tax_code' in record:
            {'tax_code': record.get('tax_code').lower()}
        return {}


class HubSaleOrderBatchImporter(Component):
    _name = 'hub.batch.sale.order.importer'
    _inherit = 'hub.batch.importer'
    _apply_on = ['hub.sale.order']

    def run(self, filters=None):
        """ Run the synchronization """
        records = self.backend_adapter.search(filters)
        tracking_ids = [r['_id']['$oid'] for r in records]
        for external_id in tracking_ids:
            self._import_record(external_id)


class HubSaleOrderImporter(Component):

    _name = 'hub.sale.order.importer'
    _inherit = 'hub.importer'
    _apply_on = ['hub.sale.order']
