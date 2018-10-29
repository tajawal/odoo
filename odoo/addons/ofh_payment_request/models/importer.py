# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

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
        return {'update_at': dt.strftime("%Y-%m-%d %H:%M:%S")}

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

    # TODO: office ID
    # TODO: Vendor ID

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

    # TODO: def entity(self, record)

    @mapping
    def order_reference(self, record) -> dict:
        if 'additionalData' in record:
            return {
                'order_reference': record['additionalData'].get('orderNumber')}
        return {}


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

    def _import_dependencies(self):
        """ Get the sale orders details related to the PR."""
        # TODO: When we have the sales order will do it through synchronisation
        order_id = self.hub_record.get('OrderId')
        if not order_id:
            return
        # request the order details from the hub
        try:
            hub_api = getattr(self.work, 'hub_api')
        except AttributeError:
            raise AttributeError(
                'You must provide a hub_api attribute with a '
                'HubAPI instance to be able to use the '
                'Backend Adapter.'
            )
        order = hub_api.get_raw_order(order_id)
        self.hub_record['airline_pnr'] = self._get_airline_pnr(
            order.get('products'))
        self.hub_record['record_locator'] = self._get_record_locator(
            order.get('products'))

    def _get_airline_pnr(self, products: list) -> str:
        if not products:
            return ''
        order_pnrs = [
            product['supplierConfirmationNumber'] for product in products
            if product['type'] in ('flight', 'hotel', 'insurance', 'package')]
        return ", ".join(set(order_pnrs))

    def _get_record_locator(self, products: list) -> str:
        if not products:
            return ''
        order_record_locators = [
            product['vendorConfirmation'] for product in products
            if product['type'] in ('flight', 'hotel', 'insurance', 'package')]
        return ", ".join(set(order_record_locators))
