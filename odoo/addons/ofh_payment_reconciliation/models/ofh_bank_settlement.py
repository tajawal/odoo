# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class OfhBankSettlement(models.Model):
    _inherit = 'ofh.bank.settlement'

    @api.multi
    def match_with_payment_gateway(self):
        """Match a bank settlement object with a Payment Gateway."""
        self.ensure_one()
        if self.matching_status not in ('matched', 'not_applicable'):
            if self.bank_name == 'sabb':
                self._match_with_payment_gateway_sabb()
            elif self.bank_name == 'rajhi':
                self._match_with_payment_gateway_rajhi()
            elif self.bank_name == 'mashreq':
                self._match_with_payment_gateway_mashreq()
            elif self.bank_name == 'amex':
                self._match_with_payment_gateway_amex()

    @api.multi
    def _match_with_payment_gateway_sabb(self):
        self.ensure_one()
        # Matching with Payment Gateway Checkout and Fort Logic
        payment_gateway_ids = self.env['ofh.payment.gateway'].search(
            [('provider', 'in', ('checkout', 'fort')),
             ('acquirer_bank', '=', self.bank_name),
             ('auth_code', '=', self.auth_code),
             ('payment_status', '=', self.payment_status)])

        if len(payment_gateway_ids):
            self.payment_gateway_id = payment_gateway_ids[0].id
            self.matching_status = 'matched'


    @api.multi
    def _match_with_payment_gateway_rajhi(self):
        self.ensure_one()
        # Matching with Payment Gateway Checkout Logic
        payment_gateway_ids = self.env['ofh.payment.gateway'].search(
            [('provider', '=', 'checkout'),
             ('acquirer_bank', '=', self.bank_name),
             ('auth_code', '=', self.auth_code),
             ('payment_status', '=', self.payment_status)])

        if len(payment_gateway_ids):
            self.payment_gateway_id = payment_gateway_ids[0].id
            self.matching_status = 'matched'

    @api.multi
    def _match_with_payment_gateway_mashreq(self):
        self.ensure_one()
        # Matching with Payment Gateway Checkout and Fort Logic
        payment_gateway_ids = self.env['ofh.payment.gateway'].search(
            [('provider', 'in', ('checkout', 'fort')),
             ('acquirer_bank', '=', self.bank_name),
             ('auth_code', '=', self.auth_code),
             ('payment_status', '=', self.payment_status)])

        if len(payment_gateway_ids):
            self.payment_gateway_id = payment_gateway_ids[0].id
            self.matching_status = 'matched'

    @api.multi
    def _match_with_payment_gateway_amex(self):
        self.ensure_one()
        # Matching with Payment Gateway Checkout Logic
        payment_gateway_ids = self.env['ofh.payment.gateway'].search(
            [('provider', '=', 'checkout'),
             ('acquirer_bank', '=', self.bank_name),
             ('auth_code', '=', self.auth_code),
             ('payment_status', '=', self.payment_status)])

        if len(payment_gateway_ids):
            self.payment_gateway_id = payment_gateway_ids[0].id
            self.matching_status = 'matched'
