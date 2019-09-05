# Copyright 2019 Seera Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import fields
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

PAYMENT_METHODS = {
    'VISA': 'visa',
    'MasterCard': 'master_card',
}
PAYMENT_STATUSES = {
    'Purchase': 'capture',
    'Credit': 'refund',
}


class BankSettlementMapper(Component):
    _inherit = 'bank.settlement.mapper'

    @mapping
    def name(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).name(record)
        return {'name': record.get("RRN")}

    @mapping
    def settlement_date(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).settlement_date(record)
        dt = datetime.strptime(record.get('Settlement Date'), '%d/%m/%Y')
        return {'settlement_date': fields.Date.to_string(dt)}

    @mapping
    def bank_name(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).bank_name(record)
        return {'bank_name': 'sabb'}

    @mapping
    def reported_mid(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).reported_mid(record)
        return {'reported_mid': record.get('Terminal ID', '')}

    @mapping
    def account_number(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).account_number(record)
        return {'account_number': record.get('Account Number', '')}

    @mapping
    def payment_method(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).payment_method(record)
        method = record.get('Card Type')
        return {'payment_method': PAYMENT_METHODS.get(method, 'none')}

    @mapping
    def is_mada(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).is_mada(record)
        if record.get('Card Type', '').lower() == 'mada':
            return {'is_mada': True}
        return {}

    @mapping
    def transaction_date(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).transaction_date(record)
        dt = datetime.strptime(
            f"{record.get('Transaction Date DD:MM:YYYY')}" 
            f"{record.get('Transaction Time')}", '%d/%m/%Y%H:%M:%S')

        return {'transaction_date': fields.Datetime.to_string(dt)}

    @mapping
    def card_number(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).card_number(record)
        return {'card_number': record.get('Card Number')}

    @mapping
    def currency_id(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).currency_id(record)

        return {'currency_id': self.env.ref('base.SAR').id}

    @mapping
    def gross_amount(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).gross_amount(record)

        return {'gross_amount': abs(float(record.get('Transaction Amount', 0.00)))}

    @mapping
    def net_transaction_amount(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).net_transaction_amount(
                record)
        return {}

    @mapping
    def merchant_charge_amount(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).merchant_charge_amount(
                record)
        return {
            'merchant_charge_amount': abs(float(record.get('Discount Amount', 0.00)))
        }

    @mapping
    def merchant_charge_vat(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).merchant_charge_vat(
                record)
        return {'merchant_charge_vat': abs(float(record.get('VAT', 0.00)))}

    @mapping
    def payment_status(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).payment_status(record)
        state = record.get('Transaction Type', '')
        return {
            'payment_status': PAYMENT_STATUSES.get(state, '')}

    @mapping
    def auth_code(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).auth_code(record)
        auth_code = record.get('Authorization Code')
        if len(auth_code) < 6:
            auth_code = auth_code.rjust(6, '0')
        return {'auth_code': auth_code}

    @mapping
    def is_3d_secure(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).is_3d_secure(record)

        if record.get('3D Secure').lower() == 'yes':
            return {'is_3d_secure': True}
        return {}

    @mapping
    def posting_date(self, record):
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementMapper, self).posting_date(record)
        dt = datetime.strptime(
            record.get('Posting Date DD:MM:YYYY'), '%d/%m/%Y')
        return {'posting_date': fields.Date.to_string(dt)}


class BankSettlementHandler(Component):
    _inherit = 'bank.settlement.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the GDS invoice line record in odoo."""
        sabb_backend = self.env.ref(
            'ofh_bank_settlement_sabb.sab_bank_settlement_import_backend')
        if self.backend_record != sabb_backend:
            return super(BankSettlementHandler, self).odoo_find_domain(
                values, orig_values)
        return [
            ('bank_name', '=', 'sabb'),
            (self.unique_key, '=', values.get('RRN'))]
