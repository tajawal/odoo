# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from odoo import fields
import json

UNIFY_STORE_ID = 1000
UNIFY_GROUP_ID = 7

class HubSaleOrderImportMapper(Component):
    _name = 'hub.sale.order.import.mapper'
    _inherit = 'hub.import.mapper'
    _apply_on = 'hub.sale.order'

    direct = [
        ('name', 'name'),
        ('track_id', 'track_id'),
        ('order_type', 'order_type'),
        ('entity', 'entity'),
        ('is_egypt', 'is_egypt'),
        ('employee_discount_tag', 'employee_discount_tag'),
        ('customer_discount_tag', 'customer_discount_tag'),
        ('ahs_group_name', 'ahs_group_name'),
        ('country_code', 'country_code'),
        ('booking_method', 'booking_method'),
        ('order_owner', 'order_owner'),
        ('is_pay_later', 'is_pay_later'),
        ('point_of_sale', 'point_of_sale'),
        ('store_id', 'store_id'),
        ('group_id', 'group_id'),
        ('total_amount', 'total_amount'),
        ('total_discount', 'total_discount'),
        ('total_output_vat', 'total_tax'),
        ('total_service_fee', 'total_service_fee'),
        ('total_insurance_amount', 'total_insurance_amount'),
        ('total_vendor_cost', 'total_vendor_cost'),
        ('total_supplier_cost', 'total_supplier_cost'),
        ('customer_email', 'customer_email'),
        ('customer_number', 'customer_number'),
        ('agent_email', 'agent_email'),
    ]
    children = [
        ('line_items', 'hub_line_ids', 'hub.sale.order.line')]

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def order_status(self, record):
        return {'order_status': str(record.get('order_status', ''))}

    @mapping
    def payment_status(self, record):
        return {'payment_status': str(record.get('payment_status', ''))}

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
    def paid_at(self, record):
        if 'paid_at' in record:
            return {'paid_at': fields.Datetime.from_string(
                    record['paid_at'])}
        return {}

    @mapping
    def vendor_currency_id(self, record):
        if 'vendor_currency' in record:
            currency = record.get('vendor_currency')
            return {'vendor_currency_id': self.env.ref(f'base.{currency}').id}
        return {}

    @mapping
    def supplier_currency_id(self, record):
        if 'supplier_currency' not in record:
            return {}

        currency = record.get('supplier_currency')
        if not currency:
            return {}
        if "," in currency:
            split_curr = currency.split(",")
            currency = split_curr[0]
        return {
            'supplier_currency_id': self.env.ref(f'base.{currency}').id}


class HubSaleOrderLineImportMapper(Component):

    _name = 'hub.sale.order.line.import.mapper'
    _inherit = 'hub.import.mapper'
    _apply_on = 'hub.sale.order.line'

    direct = [
        ('product_type', 'line_type'),
        ('product_category', 'line_category'),
        ('sequence', 'sequence'),
        ('product_id', 'name'),
        ('is_domestic_ksa', 'is_domestic_ksa'),
        ('is_domestic_uae', 'is_domestic_uae'),
        ('ahs_group_name', 'ahs_group_name'),
        ('validating_carrier', 'validating_carrier'),
        ('hotel_name', 'hotel_name'),
        ('line_id', 'external_id'),
        ('total_supplier_price', 'total_supplier_price')
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
    def vendor_base_fare_amount(self, record):
        if 'price' not in record:
            return {}
        if 'cost' not in record['price']:
            return {}
        if 'vendor' not in record['price']['cost']:
            return {}
        vendor = record['price']['cost'].get('vendor')
        base_fare = vendor.get('untaxed_amount', 0.0)
        return {'vendor_base_fare_amount': base_fare}

    @mapping
    def vendor_input_tax_amount(self, record):
        if 'price' not in record:
            return {}
        if 'cost' not in record['price']:
            return {}
        if 'vendor' not in record['price']['cost']:
            return {}
        vendor = record['price']['cost'].get('vendor')
        input_tax = vendor.get('input_vat_amount', 0.0)
        return {'vendor_input_tax_amount': input_tax}

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
    def supplier_base_fare_amount(self, record):
        if 'price' not in record:
            return {}
        if 'cost' not in record['price']:
            return {}
        if 'supplier' not in record['price']['cost']:
            return {}
        supplier = record['price']['cost'].get('supplier')
        base_fare = supplier.get('untaxed_amount', 0.0)
        return {'supplier_base_fare_amount': base_fare}

    @mapping
    def supplier_input_tax_amount(self, record):
        if 'price' not in record:
            return {}
        if 'cost' not in record['price']:
            return {}
        if 'supplier' not in record['price']['cost']:
            return {}
        supplier = record['price']['cost'].get('supplier')
        input_tax = supplier.get('input_vat_amount', 0.0)
        return {'supplier_input_tax_amount': input_tax}

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
    def line_reference(self, record):
        if record.get('product_type').lower() == 'flight':
            if 'traveller' not in record:
                return {}
            line_reference = record['traveller'].get('line_reference')
        else:
            if 'segment' not in record:
                return {}
            line_reference = str(record['segment'].get('line_reference'))

        return {'line_reference': line_reference}

    @mapping
    def office_id(self, record):
        if record.get('product_type').lower() != 'flight':
            return {}
        if 'traveller' not in record:
            return {}
        if 'office' not in record['traveller']:
            return {}
        office = record['traveller'].get('office')
        return {'office_id': office.get('office_id')}

    @mapping
    def ticketing_office_id(self, record):
        if record.get('product_type').lower() != 'flight':
            return {}
        if 'traveller' not in record:
            return {}
        if 'office' not in record['traveller']:
            return {}
        office = record['traveller'].get('office')
        return {'ticketing_office_id': office.get('ticketing_office_id')}

    @mapping
    def tour_code_office_id(self, record):
        if record.get('product_type').lower() != 'flight':
            return {}
        if 'traveller' not in record:
            return {}
        if 'office' not in record['traveller']:
            return {}
        office = record['traveller'].get('office')
        return {'tour_code_office_id': office.get('tour_code_office_id')}

    @mapping
    def contract(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'segment' not in record:
            return {}
        if 'hotel' not in record['segment']:
            return {}
        hotel = record['segment'].get('hotel')
        return {'contract': hotel.get('contract')}

    @mapping
    def hotel_id(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'segment' not in record:
            return {}
        if 'hotel' not in record['segment']:
            return {}
        hotel = record['segment'].get('hotel')
        return {'hotel_id': hotel.get('hotel_id')}

    @mapping
    def hotel_country(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'segment' not in record:
            return {}
        if 'hotel' not in record['segment']:
            return {}
        hotel = record['segment'].get('hotel')
        return {'hotel_country': hotel.get('country')}

    @mapping
    def hotel_city(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'segment' not in record:
            return {}
        if 'hotel' not in record['segment']:
            return {}
        hotel = record['segment'].get('hotel')
        return {'hotel_city': hotel.get('city')}

    @mapping
    def hotel_supplier_id(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'segment' not in record:
            return {}
        if 'hotel' not in record['segment']:
            return {}
        hotel = record['segment'].get('hotel')
        return {'hotel_supplier_id': hotel.get('supplier_id')}

    @mapping
    def check_in_date(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'segment' not in record:
            return {}
        check_in_date = record['segment'].get('check_in_date')
        return {
            'check_in_date': fields.Datetime.from_string(check_in_date)
        }

    @mapping
    def checkout_date(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'segment' not in record:
            return {}
        checkout_date = record['segment'].get('checkout_date')
        return {'checkout_date': fields.Datetime.from_string(checkout_date)}

    @mapping
    def nb_nights(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'segment' not in record:
            return {}
        nb_nights = record['segment'].get('nb_nights')
        return {'nb_nights': nb_nights}

    @mapping
    def nb_rooms(self, record):
        if record.get('product_type').lower() != 'hotel':
            return {}
        if 'segment' not in record:
            return {}
        nb_rooms = record['segment'].get('nb_rooms')
        return {'nb_rooms': nb_rooms}

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
            return {'tax_code': record.get('tax_code').lower()}
        return {}

    @mapping
    def state(self, record):
        return {'state': str(record['line_status'])}

    @mapping
    def passengers_count(self, record):
        if 'traveller' in record:
            return {
                'passengers_count': record['traveller'].get(
                    'nb_passengers')}
        if 'segment' in record:
            return {
                'passengers_count': record['segment'].get('nb_passengers')
            }

        return {}

    @mapping
    def last_leg_flying_date(self, record):
        if 'traveller' in record:
            return {
                'last_leg_flying_date': record['traveller'].get(
                    'last_leg_flying_date', '')}
        return {}

    @mapping
    def segment_count(self, record):
        if 'traveller' in record:
            return {
                'segment_count': record['traveller'].get('segment_count', '')
            }
        if 'segment' in record:
            return {
                'segment_count': record['segment'].get('segment_count', '')
            }
        return {}

    @mapping
    def destination_city(self, record):
        if 'traveller' in record:
            return {
                'destination_city': record['traveller'].get(
                    'destination_city', '')}

    @mapping
    def origin_city(self, record):
        if 'traveller' in record:
            return {
                'origin_city': record['traveller'].get(
                    'origin_city', '')}
        return {}

    @mapping
    def booking_class(self, record):
        if 'traveller' in record:
            return {
                'booking_class': record['traveller'].get(
                    'booking_class', '')}
        return {}

    @mapping
    def departure_date(self, record):
        if 'traveller' in record:
            return {
                'departure_date': record['traveller'].get(
                    'departure_date', '')}
        return {}

    @mapping
    def route(self, record):
        if 'traveller' in record:
            return {
                'route': record['traveller'].get('route', '')}
        return {}

    @mapping
    def segments(self, record):
        if 'traveller' in record:
            return {
                'segments': json.dumps(record['traveller'].get('segments', ''))
            }
        return {}


class HubSaleOrderBatchImporter(Component):
    _name = 'hub.batch.sale.order.importer'
    _inherit = 'hub.batch.importer'
    _apply_on = ['hub.sale.order']

    def run(self, filters=None):
        """ Run the synchronization """
        records = self.backend_adapter.search(filters)
        for record in records:
            self._import_record(record['_id']['$oid'])


class HubSaleOrderImporter(Component):

    _name = 'hub.sale.order.importer'
    _inherit = 'hub.importer'
    _apply_on = ['hub.sale.order']

    def _is_uptodate(self, binding) -> bool:
        if not binding:
            return False    # The record has never been synchronised.

        assert self.hub_record

        sync_date = fields.Datetime.from_string(binding.sync_date)
        hub_date = fields.Datetime.from_string(
            self.hub_record.get('updated_at'))

        return hub_date < sync_date


class HubSaleOrderLineImportMapChild(Component):
    _name = 'map.child.hub.sale.order.line.import'
    _inherit = 'base.map.child.import'
    _apply_on = 'hub.sale.order.line'

    def format_items(self, items_values):
        """
        Format the values of the items mapped from the child Mappers.

        It can be overridden for instance to add the Odoo
        relationships commands ``(6, 0, [IDs])``, ...

        As instance, it can be modified to handle update of existing
        items: check if an 'id' has been defined by
        :py:meth:`get_item_values` then use the ``(1, ID, {values}``)
        command

        :param items_values: list of values for the items to create
        :type items_values: list

        """
        items = []
        for values in items_values:
            if 'external_id' not in values:
                continue
            binding = self.model.search(
                [('external_id', '=', values.get('external_id'))])
            if binding:
                items.append((1, binding.id, values))
                continue
            else:
                items.append((0, 0, values))

        return items
