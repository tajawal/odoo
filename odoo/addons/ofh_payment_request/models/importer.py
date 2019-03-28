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
    def payment_mode(self, record):
        if 'response' not in record:
            return {}
        if 'metadata' not in record['response']:
            return {}
        return {
            'payment_mode': record['response']['metadata'].get('paymentMode')
        }

    @mapping
    def is_egypt(self, record):
        app_details = record.get('app_details')
        if not app_details:
            return {}
        return {'is_egypt': app_details.get('is_almosafer_egypt', False)}


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
        # TODO: remove when we switch to oms-finance-api endpoint.
        if 'additionalData' in record:
            store_id = record['additionalData'].get('storeId')
            if store_id:
                record['app_details'] = hub_api.get_raw_store(int(store_id))

        return record
