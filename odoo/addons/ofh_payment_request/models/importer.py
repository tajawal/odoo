# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
import logging

from odoo import fields
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
UNIFY_STORE_ID = 1000
UNIFY_GROUP_ID = 7

_logger = logging.getLogger(__name__)


class HubPaymentRequestImportMapper(Component):
    _name = 'hub.payment.request.import.mapper'
    _inherit = 'hub.import.mapper'
    _apply_on = 'hub.payment.request'

    direct = [
        ('request_type', 'request_type'),
        ('status', 'request_status'),
        ('processed_by', 'processed_by'),
        ('reason', 'request_reason'),
        ('track_id', 'track_id'),
        ('parent_track_id', 'parent_track_id'),
        ('auth_code', 'auth_code'),
        ('remarks', 'notes'),
        ('payment_mode', 'payment_mode'),
        ('total_amount', 'total_amount'),
    ]

    children = [
        ('payments', 'hub_payment_ids', 'hub.payment')]

    @mapping
    def created_at(self, record) -> dict:
        dt = fields.Datetime.from_string(record['created_at'])
        return {'created_at': dt}

    @mapping
    def updated_at(self, record) -> dict:
        dt = fields.Datetime.from_string(record['updated_at'])
        return {'updated_at': dt}

    @mapping
    def request_date(self, record) -> dict:
        """ SHould convert date """

    @mapping
    def currency_id(self, record) -> dict:
        if 'currency' in record:
            currency = self.env['res.currency'].search(
                [('name', '=', record['currency'])], limit=1)
            if currency:
                return {'currency_id': currency.id}
        return {'currency_id': self.env.ref('base.AED').id}

    @mapping
    def fees(self, record) -> dict:
        if 'fees' in record:
            return {'fees': json.dumps(record.get('fees'))}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def matching_status(self, record):
        order_reference = record.get('order_reference')
        if order_reference.startswith('H'):
            return {'matching_status': 'not_applicable'}
        return {}


class HubPaymentRequestBatchImporter(Component):
    _name = 'hub.batch.payment.request.importer'
    _inherit = 'hub.batch.importer'
    _apply_on = ['hub.payment.request']

    def run(self, filters=None):
        """ Run the synchronization """
        records = self.backend_adapter.search(filters)
        for record in records:
            store_id = record['additionalData'].get('storeId', '')
            track_id = record['additionalData'].get('trackId', '')
            pr_type = record.get('type', '')
            backend = self.env['hub.backend'].search([], limit=1)

            # Online Charge Payment Request => Create Sale Order and payment
            if store_id != UNIFY_STORE_ID and pr_type == 'charge':
                with backend.work_on('hub.sale.order') as work:
                    importer = work.component(usage='record.importer')
                    importer.run(track_id, force=False)

            # Unify Charge Payment Request => Create payment only
            if store_id == UNIFY_STORE_ID and pr_type == 'charge':
                with backend.work_on('hub.payment') as work:
                    importer = work.component(usage='record.importer')
                    importer.run(track_id, force=False)

            # Online and Unify Refund Payment Request => Create payment request
            if pr_type == 'refund':
                self._import_record(track_id)


class HubPaymentRequestImporter(Component):
    _name = 'hub.payment.request.importer'
    _inherit = 'hub.importer'
    _apply_on = ['hub.payment.request']

    def _is_uptodate(self, binding) -> bool:
        """Check if record is already up-to-date.

        Arguments:
            binding {hub.binder} -- [Binder instance for hub records]

        Returns:
            bool -- Return True if the import should be skipped else False
        """
        if not binding:
            return False  # The record has never been synchronised.

        assert self.hub_record

        sync_date = fields.Datetime.from_string(binding.sync_date)
        hub_date = fields.Datetime.from_string(
            self.hub_record.get('updated_at'))

        return hub_date < sync_date

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
