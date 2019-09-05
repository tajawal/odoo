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
    'PRCH': 'capture',
    'RFND': 'refund',
}


class BankSettlementMapper(Component):
    _inherit = 'bank.settlement.mapper'

    @mapping
    def name(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).name(record)
        return {'name': record.get("ARN")}

    @mapping
    def settlement_date(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).settlement_date(record)
        dt = datetime.strptime(record.get('Settlement Date'), '%d/%m/%Y')
        return {'settlement_date': fields.Date.to_string(dt)}

    @mapping
    def bank_name(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).bank_name(record)
        return {'bank_name': 'amex'}

    @mapping
    def reported_mid(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).reported_mid(record)
        return {'reported_mid': ''}

    @mapping
    def account_number(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).account_number(record)
        return {'account_number': ''}

    @mapping
    def payment_method(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).payment_method(record)
        return {'payment_method': ''}

    @mapping
    def is_mada(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).is_mada(record)
        return {}

    @mapping
    def transaction_date(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).transaction_date(record)
        return {}

    @mapping
    def card_number(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).card_number(record)
        return {'card_number': record.get('Card Number')}

    @mapping
    def currency_id(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).currency_id(record)
        currency = record.get('CURRENCY', '')
        return {'currency_id': self.env.ref('base.' + currency.upper()).id}

    @mapping
    def gross_amount(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).gross_amount(record)

        return {'gross_amount': abs(float(record.get('Submission Amount', 0.00)))}

    @mapping
    def net_transaction_amount(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).net_transaction_amount(
                record)
        return {'net_transaction_amount': abs(float(record.get('Net Amount', 0.00)))}

    @mapping
    def merchant_charge_amount(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).merchant_charge_amount(
                record)
        return {
            'merchant_charge_amount': abs(float(record.get('Discount Amount', 0.00)))
        }

    @mapping
    def merchant_charge_vat(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).merchant_charge_vat(
                record)
        return {'merchant_charge_vat': ''}

    @mapping
    def payment_status(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).payment_status(record)
        vos = record.get('Submission Amount', 0.00)
        if vos >= 0:
            return {'payment_status': 'capture'}
        else:
            return {'payment_status': 'refund'}

    @mapping
    def auth_code(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).auth_code(record)
        auth_code = record.get('Approval Code')
        if len(auth_code) < 6:
            auth_code = auth_code.rjust(6, '0')
        return {'auth_code': auth_code}

    @mapping
    def is_3d_secure(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).is_3d_secure(record)
        return {}

    @mapping
    def posting_date(self, record):
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementMapper, self).posting_date(record)
        return {'posting_date': ''}


class BankSettlementHandler(Component):
    _inherit = 'bank.settlement.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the GDS invoice line record in odoo."""
        amex_backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        if self.backend_record != amex_backend:
            return super(BankSettlementHandler, self).odoo_find_domain(
                values, orig_values)
        return [
            ('bank_name', '=', 'amex'),
            (self.unique_key, '=', values.get('ARN'))]
