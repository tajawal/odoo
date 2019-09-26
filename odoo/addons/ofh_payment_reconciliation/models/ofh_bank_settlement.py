# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class OfhBankSettlement(models.Model):
    _inherit = 'ofh.bank.settlement'

    payment_gateway_id = fields.Many2one(
        string="Payment Gateway Id",
        comodel_name='ofh.payment.gateway',
        required=False,
        ondelete='cascade',
        track_visibility='onchange',
    )
    matching_status = fields.Selection(
        string="Matching Status",
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable')],
        default='unmatched',
        required=True,
        index=True,
        readonly=True,
        track_visibility='onchange',
    )
    reconciliation_status = fields.Selection(
        string="Reconciliation Status",
        selection=[
            ('reconciled', 'Reconciled'),
            ('unreconciled', 'Unreconciled'),
            ('not_applicable', 'Not Applicable'),
        ],
        default='unreconciled',
        compute='_compute_reconciliation_amount',
        index=True,
        readonly=True,
        track_visibility='onchange',
    )
    reconciliation_tag = fields.Char(
        string="Reconciliation Tag",
        track_visibility='onchange',
    )
    reconciliation_amount = fields.Monetary(
        string="Reconciliation Amount",
        compute='_compute_reconciliation_amount',
        currency_field='currency_id',
        readonly=True,
        store=False,
    )

    @api.multi
    @api.depends(
        'payment_gateway_id.total', 'matching_status',
        'gross_amount', 'reconciliation_tag')
    def _compute_reconciliation_amount(self):
        for rec in self:
            rec.reconciliation_amount = 0

            if rec.matching_status == 'unmatched':
                rec.reconciliation_status = 'unreconciled'
                continue

            if rec.matching_status == 'not_applicable':
                rec.reconciliation_status = 'not_applicable'
                continue

            rec.reconciliation_amount = \
                abs(rec.payment_gateway_id.total - rec.gross_amount)

            if rec.reconciliation_tag:
                rec.reconciliation_status = 'reconciled'
                continue

            if rec.reconciliation_amount <= 1:
                rec.reconciliation_status = 'reconciled'
            else:
                rec.reconciliation_status = 'unreconciled'

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
