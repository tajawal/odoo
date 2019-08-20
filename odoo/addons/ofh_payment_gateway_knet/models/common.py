# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from odoo import fields

PAYMENT_STATUSES = {
    'Captured': 'capture',
}


class PaymentGatewayMapper(Component):
    _inherit = 'payment.gateway.mapper'

    @mapping
    def name(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).name(record)
        return {'name': record.get('ACTION ID')}

    @mapping
    def provider(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).provider(record)
        return {'provider': 'knet'}

    @mapping
    def acquirer_bank(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).acquirer_bank(record)
        return {'acquirer_bank': 'sabb'}

    @mapping
    def track_id(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).track_id(record)
        return {'track_id': record.get('REFERENCE')}

    @mapping
    def auth_code(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).auth_code(record)
        return {'auth_code': record.get('AUTH CODE')}

    @mapping
    def payment_method(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).payment_method(record)
        return {'payment_method': record.get('PAYMENT METHOD')}

    @mapping
    def transaction_date(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).transaction_date(record)
        # TODO: correct the format 6/30/2019 11:45:23 PM
        dt = datetime.strptime(record.get('ACTION DATE'), '%m/%d/%Y %H:%M:%S')
        return {'transaction_date': fields.Date.to_string(dt)}

    @mapping
    def total(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).total(record)
        return {'total': float(record.get('AMOUNT'))}

    @mapping
    def currency_id(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).currency_id(record)
        currency = record.get('CURRENCY')
        if not currency:
            return {}
        return {'currency_id': self.env.ref('base.{}'.format(currency)).id}

    @mapping
    def payment_status(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).payment_status(record)
        state = record.get('RESPONSE DESCRIPTION')
        return {'payment_status': PAYMENT_STATUSES.get(state, '')}

    @mapping
    def card_name(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).card_name(record)
        return {'card_name': record.get('CARD HOLDER NAME')}

    @mapping
    def card_number(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).card_number(record)
        return {'card_number': record.get('CC NUMBER')}

    @mapping
    def card_bin(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).card_bin(record)
        return {'card_bin': record.get('CC BIN')}

    @mapping
    def card_bank(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).card_bank(record)
        return {'card_bank': record.get('ISSUING BANK')}

    @mapping
    def card_expiry_year(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).card_expiry_year(record)
        return {'card_expiry_year': record.get('EXPIRY YEAR')}

    @mapping
    def card_expiry_month(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).card_expiry_month(record)
        return {'card_expiry_month': record.get('EXPIRY MONTH')}

    @mapping
    def response_description(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).response_description(
                record)
        return {'response_description': record.get('RESPONSE DESCRIPTION')}

    @mapping
    def customer_email(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).customer_email(record)
        return {'customer_email': record.get('CUSTOMER EMAIL')}

    @mapping
    def is_3d_secure(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).is_3d_secure(record)
        return {'is_3d_secure': record.get('3D SECURE PAYMENT')}

    @mapping
    def arn(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).arn(record)
        return {'arn': record.get('ACQUIRER REFERENCE ID')}

    @mapping
    def reported_mid(self, record):
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayMapper, self).reported_mid(record)
        return {'reported_mid': record.get('MID')}


class PaymentGatewayRecordImporter(Component):
    _name = 'payment.gateway.record.importer'
    _inherit = 'importer.record'
    _apply_on = ['ofh.payment.gateway']

    odoo_unique_key = 'name'

    def required_keys(self, create=False):
        """Keys that are mandatory to import a line."""
        return {}

    def run(self, record, **kw):
        result = super(PaymentGatewayRecordImporter, self).run(
            record, **kw)
        msg = ' '.join([
            '{} import chunk completed'.format(
                self.tracker.log_prefix.upper()),
            '[created: {created}]',
            '[updated: {updated}]',
            '[skipped: {skipped}]',
            '[errored: {errored}]',
        ]).format(**self.tracker.get_counters())
        self.env.user.notify_info(msg)
        return result


class PaymentGatewayHandler(Component):
    _inherit = 'payment.gateway.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the GDS invoice line record in odoo."""
        knet_backend = self.env.ref(
            'ofh_payment_gateway_knet.knet_import_backend')
        if self.backend_record != knet_backend:
            return super(PaymentGatewayHandler, self).odoo_find_domain(
                values, orig_values)
        return [
            ('provider', '=', 'checkout'),
            (self.unique_key, '=', values.get('Action ID'))]
