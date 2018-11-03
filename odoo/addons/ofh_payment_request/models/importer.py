# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
import json

PROCESSED_HUB_STATUS = 'Processed'


class HubPaymentRequestImportMapper(Component):
    _name = 'hub.payment.request.import.mapper'
    _inherit = 'hub.import.mapper'
    _apply_on = 'hub.payment.request'

    direct = [
        ('type', 'request_type'),
        ('status', 'request_status'),
        ('orderId', 'order_id'),
        ('airline_pnr', 'pnr'),
        ('record_locator', 'record_locator'),
        ('airline_code', 'vendor_id'),
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
        return self.hub_record.get('status') != PROCESSED_HUB_STATUS

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
        record['airline_pnr'] = self._get_airline_pnr(order.get('products'))
        record['record_locator'] = self._get_record_locator(
            order.get('products'))
        record['airline_code'] = self._get_airline_code(order.get('products'))
        return record

    def _get_airline_pnr(self, products: list) -> str:
        if not products:
            return ''
        order_pnrs = [
            product.get('supplierConfirmationNumber', '')
            for product in products
            if product['type'] in ('flight', 'hotel', 'insurance', 'package')]
        return ", ".join(set(order_pnrs))

    def _get_record_locator(self, products: list) -> str:
        if not products:
            return ''
        order_record_locators = [
            product.get('vendorConfirmationNumber', '') for product in products
            if product['type'] in ('flight', 'hotel', 'insurance', 'package')]
        return ", ".join(set(order_record_locators))

    def _get_airline_code(self, products: list) -> str:
        if not products:
            return ''
        airline_codes = [
            product.get('supplierName', '') for product in products
            if product['type'] == 'flight']
        return ", ".join(set(airline_codes))
