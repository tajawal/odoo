# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
import logging
from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

PROCESSED_HUB_STATUSES = \
    ('Processed', 'Processed Manually', 'Customer Processed')
ORDER_STATUS_MANUALLY_CONFIRMED = 53
ORDER_STATUS_MANUALLY_ORDERED = 51
ORDER_STATUS_AUTO_CONFIRMED = 58
ORDER_STATUS_REFUNDED = 95
ORDER_STATUS_CANCELED = 94
ORDER_STATUS_MANUALLY_CANCELLED = 96

_logger = logging.getLogger(__name__)


class HubPaymentRequestImportMapper(Component):
    _name = 'hub.payment.request.import.mapper'
    _inherit = 'hub.import.mapper'
    _apply_on = 'hub.payment.request'

    direct = [
        ('type', 'request_type'),
        ('status', 'request_status'),
        ('orderId', 'order_id'),
        ('airline_code', 'vendor_id'),
        ('order_supplier_cost', 'order_supplier_cost'),
        ('order_amount', 'order_amount'),
        ('order_type', 'order_type'),
        ('hub_supplier_reference', 'hub_supplier_reference'),
        ('plan_code', 'plan_code'),
        ('order_discount', 'order_discount'),
        ('order_created_at', 'order_created_at'),
        ('order_updated_at', 'order_updated_at'),
    ]

    @mapping
    def created_at(self, record) -> dict:
        dt = datetime.fromtimestamp(
            int(record['createdAt']['$date'].get('$numberLong')) / 1000)
        return {'created_at': dt.strftime("%Y-%m-%d %H:%M:%S")}

    @mapping
    def updated_at(self, record) -> dict:
        dt = datetime.fromtimestamp(
            int(record['updatedAt']['$date'].get('$numberLong')) / 1000)
        return {'updated_at': dt.strftime("%Y-%m-%d %H:%M:%S")}

    @mapping
    def request_reason(self, record) -> dict:
        if 'additionalData' in record:
            return {'request_reason': record['additionalData'].get('reason')}
        return {}

    @mapping
    def request_date(self, record) -> dict:
        """ SHould convert date """

    @mapping
    def charge_id(self, record) -> dict:
        if 'response' in record:
            return {'charge_id': record['response'].get('chargeId')}
        return {}

    @mapping
    def track_id(self, record) -> dict:
        if 'additionalData' in record:
            return {'track_id': record['additionalData'].get('trackId')}
        return {}

    @mapping
    def auth_code(self, record) -> dict:
        if 'response' in record:
            return {'auth_code': record['response'].get('authCode')}
        return {}

    @mapping
    def currency_id(self, record) -> dict:
        if 'currency' in record:
            currency = self.env['res.currency'].search(
                [('name', '=', record.get('currency'))], limit=1)
            if currency:
                return {'currency_id': currency.id}
        return {'currency_id': self.env.ref('base.AED').id}

    @mapping
    def order_supplier_currency(self, record) -> dict:
        if 'order_supplier_currency' in record:
            currency = self.env['res.currency'].search(
                [('name', '=', record.get('order_supplier_currency'))],
                limit=1)
            if currency:
                return {'order_supplier_currency': currency.id}

    @mapping
    def total_amount(self, record) -> dict:
        if 'fees' in record:
            return {'total_amount': record['fees'].get('total')}
        return {'total_amount': 0.0}

    @mapping
    def fees(self, record) -> dict:
        if 'fees' in record:
            return {'fees': json.dumps(record.get('fees'))}

    @mapping
    def order_reference(self, record) -> dict:
        if 'additionalData' in record:
            return {
                'order_reference': record['additionalData'].get('orderNumber')}
        return {}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def notes(self, record):
        if 'additionalData' in record:
            return {'notes': record['additionalData'].get('remarks')}
        return {}

    @mapping
    def entity(self, record):
        if 'app_details' in record:
            return {'entity': record['app_details'].get('site')}

    @mapping
    def reconciliation_status(self, record):
        order_type = record.get('order_type')
        locator = record.get('hub_supplier_reference')
        if order_type == 'hotel' or not locator:
            return {'reconciliation_status': 'not_applicable'}
        return {}

    @mapping
    def provider(self, record):
        if 'response' in record:
            return {'provider': record['response'].get('provider')}
        return {}

    @mapping
    def payment_method(self, record):
        if 'response' not in record:
            return {}
        if 'metadata' not in record['response']:
            return {}
        return {
            'payment_method': record['response']['metadata'].get('paymentMode')
        }


class HubPaymentRequestBatchImporter(Component):
    _name = 'hub.batch.payment.request.importer'
    _inherit = 'hub.batch.importer'
    _apply_on = ['hub.payment.request']

    def run(self, filters=None):
        """ Run the synchronization """
        records = self.backend_adapter.search(filters)
        tracking_ids = [r['additionalData']['trackId'] for r in records]
        for external_id in tracking_ids:
            self._import_record(external_id)


class HubPaymentRequestImporter(Component):
    _name = 'hub.payment.request.importer'
    _inherit = 'hub.importer'
    _apply_on = ['hub.payment.request']

    def _must_skip(self) -> bool:
        """ For payment request we process only records that are already
        been processed.

        Returns:
            bool -- True if the record should be skipped else False
        """
        return self.hub_record.get('status') not in PROCESSED_HUB_STATUSES

    def _get_hub_data(self):
        """ Return the raw hub data for ``self.external_id `` """
        record = self.backend_adapter.read(self.external_id)
        try:
            hub_api = getattr(self.work, 'hub_api')
        except AttributeError:
            raise AttributeError(
                'You must provide a hub_api attribute with a '
                'HubAPI instance to be able to use the '
                'Backend Adapter.'
            )

        # Get the entity using the config API to get all the store details
        if 'additionalData' in record:
            store_id = record['additionalData'].get('storeId')
            if store_id:
                record['app_details'] = hub_api.get_raw_store(int(store_id))

        # This should be done in the dependency method when we have the
        # sale order integration, for now we will have it here.
        order_id = record.get('orderId')
        if not order_id:
            return record

        order = hub_api.get_raw_order(order_id)
        record['order_type'] = order.get('type')
        record['order_created_at'] = order.get('createdAt')
        record['order_updated_at'] = order.get('updatedAt')
        record['order_amount'] = order['totals']['total']
        record['order_supplier_cost'], record['order_supplier_currency'] = \
            self._get_order_supplier_details(order.get('products'))
        record['hub_supplier_reference'] = self._get_supplier_reference(
            order.get('products'))
        record['plan_code'] = self._get_plan_code(order.get('products'))
        record['airline_code'] = self._get_airline_code(order.get('products'))
        record['order_discount'] = self._get_order_discount(
            order.get('products'))
        return record

    def _get_supplier_reference(self, products: list) -> str:
        if not products:
            return ''
        supplier_references = [
            product.get('vendorConfirmationNumber', '')
            for product in products if product['type'] in
            ('flight', 'hotel', 'insurance', 'package')]
        supplier_references.extend([
            product.get('supplierConfirmationNumber', '')
            for product in products if product['type'] in
            ('flight', 'hotel', 'insurance', 'package')])
        return ",".join(set([r for r in supplier_references]))

    def _get_plan_code(self, products: list) -> str:
        if not products:
            return ''
        plan_codes = [
            product['options'].get('plan_code') for product in products if
            product.get('options') and product['type'] == 'insurance']
        return ", ".join(set([p for p in plan_codes if p]))

    def _get_airline_code(self, products: list) -> str:
        if not products:
            return ''
        airline_codes = [
            product.get('supplierName', '') for product in products
            if product['type'] == 'flight']
        return ", ".join(set(airline_codes))

    def _get_order_supplier_details(self, products: list) -> tuple:
        """Get supplier cost details from order related to the payment request.

        Arguments:
            products {list} -- Product list from the order dictionary

        Returns:
            tuple -- (supplier amount, supplier currency)
        """
        # TODO for now i'm keeping the calculation very simple, when we will
        # have the sale orders in the platform the calculation will be diffrent
        # and easier.
        supplier_amount = net_price = 0
        supplier_currency = net_price_currency = ''
        for product in products:
            # We skip fail orders
            if product['status'] not in (
               ORDER_STATUS_MANUALLY_CONFIRMED, ORDER_STATUS_AUTO_CONFIRMED,
               ORDER_STATUS_MANUALLY_ORDERED, ORDER_STATUS_MANUALLY_ORDERED,
               ORDER_STATUS_REFUNDED):
                continue
            # This calculation is only needed for hotels for now, to be used
            # in reverse calculation
            if product['type'] != 'hotel':
                continue
            supplier_name = product.get('supplierName')

            # Expedia Hotels will use net price
            if product['additionalData'].get('netPrice'):
                net_price += product['additionalData']['netPrice'].get('price')
                net_price_currency = \
                    product['additionalData']['netPrice'].get('currency')

            if product['additionalData'].get('financeReport'):
                for freport in product['additionalData']['financeReport']:
                    segments = freport.get('Segments')
                    segments_count = len(segments)
                    for segment in segments:
                        supplier_currency = segment.get('SupplierCurrency')
                        supplier_amount += segment.get(
                            'PriceInSupplierCurrency', 0)
                        if supplier_name == 'Expedia':
                            supplier_amount += (net_price / segments_count)
                            if net_price_currency:
                                supplier_currency = net_price_currency

        return (supplier_amount, supplier_currency)

    def _get_order_discount(self, products: list) -> float:
        discount = 0.0
        for product in products:
            if product['type'] not in ('rule', 'coupon'):
                continue
            if product['type'] == 'coupon':
                discount += product['price']['total']
            elif product['price']['total'] < 0:
                discount += product['price']['total']
        return discount
