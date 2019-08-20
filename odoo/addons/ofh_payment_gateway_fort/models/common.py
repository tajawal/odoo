# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from odoo import fields

ACQUIRER_BANK = {
    'Commercial International Bank (CIB)': 'cib',
    'The Saudi British Bank (SABB)': 'sabb'
}

PAYMENT_STATUSES = {
    'Capture': 'capture',
    'Authorization': 'auth',
    'Refund': 'refund',
}

FORT_MIDS_BY_CURRENCY = {
    'AED': '80537',
    'SAR': '80096'
}


class PaymentGatewayMapper(Component):
    _inherit = 'payment.gateway.mapper'

    @mapping
    def name(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).name(record)
        reference = f"{record.get('FORT ID')}_{record.get('Operation', '')}"
        return {'name': reference}

    @mapping
    def provider(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).provider(record)
        return {'provider': 'fort'}

    @mapping
    def acquirer_bank(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).acquirer_bank(record)
        acquirer_bank = record.get('Acquirer Name')
        return {'acquirer_bank': ACQUIRER_BANK.get(acquirer_bank, 'mashreq')}

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
        return {'payment_method': record.get('Payment Option')}

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
        state = record.get('Operation', '')
        return {'payment_status': PAYMENT_STATUSES.get(state, '')}

    @mapping
    def reported_mid(self, record):
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')
        if self.backend_record != fort_backend:
            return super(PaymentGatewayMapper, self).reported_mid(record)
        currency = record.get('Currency')
        return {'reported_mid': FORT_MIDS_BY_CURRENCY.get(currency, '')}


class PaymentGatewayHandler(Component):
    _inherit = 'payment.gateway.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the GDS invoice line record in odoo."""
        fort_backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')

        if self.backend_record != fort_backend:
            return super(PaymentGatewayHandler, self).odoo_find_domain(
                values, orig_values)
        return [
            ('provider', '=', 'fort'),
            (self.unique_key, '=', values.get('FORT ID'))]
