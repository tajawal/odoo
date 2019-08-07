# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from odoo import fields


class PaymentGatewayMapper(Component):
    _inherit = 'payment.gateway.mapper'

    @mapping
    def created_at(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).created_at(record)
        return {'created_at': datetime.today().strftime("%d-%m-%y")}

    @mapping
    def updated_at(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).updated_at(record)
        return {'updated_at': datetime.today().strftime("%d-%m-%y")}

    @mapping
    def name(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).name(record)
        return {'name': 'fort'}

    @mapping
    def provider(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).provider(record)
        return {'provider': 'fort'}

    @mapping
    def payment_gateway_id(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).payment_gateway_id(record)
        return {'payment_gateway_id': record.get('FORT ID')}

    @mapping
    def acquirer_bank(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).acquirer_bank(record)
        aquirer_bank = record.get('Acquirer Name')
        if aquirer_bank == 'Commercial International bank':
            return {'acquirer_bank': 'cib'}
        elif aquirer_bank == 'Mashreq':
            return {'acquirer_bank': 'mashreq'}
        elif aquirer_bank == 'The Saudi British Bank':
            return {'acquirer_bank': 'sabb'}

    @mapping
    def track_id(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).track_id(record)
        return {'track_id': record.get('Merchant Reference')}

    @mapping
    def auth_code(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).auth_code(record)
        return {'auth_code': record.get('Authorization Code')}

    @mapping
    def payment_method(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).payment_method(record)
        return {'payment_method': record.get('Payment Method')}

    @mapping
    def payment_by(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).payment_by(record)
        return {'payment_by': record.get('Payment Method')}

    @mapping
    def transaction_date(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).transaction_date(record)
        # TODO: correct the format 6/30/2019 11:45:23 PM
        dt = datetime.strptime(record.get('Date & Time'), '%m/%d/%y %H:%M')
        return {'transaction_date': fields.Date.to_string(dt)}

    @mapping
    def total(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).total(record)
        return {'total': float(record.get('Amount'))}

    @mapping
    def currency_id(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).currency_id(record)
        currency = record.get('Currency')
        if not currency:
            return {}
        return {'currency_id': self.env.ref('base.{}'.format(currency)).id}

    @mapping
    def payment_status(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).payment_status(record)
        return {'payment_status': record.get('Operation')}

    @mapping
    def card_name(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).card_name(record)
        return {}

    @mapping
    def card_number(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).card_number(record)
        return {}

    @mapping
    def card_bin(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).card_bin(record)
        return {}

    @mapping
    def card_bank(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).card_bank(record)
        return {}

    @mapping
    def card_type(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).card_type(record)
        return {}

    @mapping
    def card_wallet_type(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).card_wallet_type(record)
        return {}

    @mapping
    def card_expiry_year(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).card_expiry_year(record)
        return {}

    @mapping
    def card_expiry_month(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).card_expiry_month(record)
        return {}

    @mapping
    def response_description(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).response_description(record)
        return {}

    @mapping
    def customer_email(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).customer_email(record)
        return {}

    @mapping
    def cvv_check(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).cvv_check(record)
        return {}

    @mapping
    def is_3d_secure(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).is_3d_secure(record)
        return {}

    @mapping
    def arn(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).fort_backend(record)
        return {}

    @mapping
    def payment_id(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).payment_id(record)
        return {}

    @mapping
    def server_ip(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).server_ip(record)
        return {}

    @mapping
    def reported_mid(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).reported_mid(record)
        currency = record.get('Currency')
        crr = {}
        if currency == 'AED':
            crr = {'reported_mid': '80537'}
        if currency == 'SAR':
            crr = {'reported_mid': '80096'}
        return crr


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
    _inherit = 'importer.odoorecord.handler'
    _name = 'payment.gateway.handler'
    _apply_on = ['ofh.payment.gateway']
