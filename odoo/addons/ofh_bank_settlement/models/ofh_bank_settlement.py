# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class OfhBankSettlement(models.Model):
    _name = 'ofh.bank.settlement'
    _description = "Bank Settlement"
    _rec_name = 'name'

    name = fields.Char(
        string="ARN",
        readonly=True,
        required=True,
    )
    settlement_date = fields.Date(
        string="Settlement Date",
        readonly=True,
    )
    bank_name = fields.Selection(
        string="Bank Name",
        selection=[],
        required=True,
        readonly=True,
        index=True,
    )
    reported_mid = fields.Char(
        string="Reported MID",
        required=True,
        readonly=True,
    )
    account_number = fields.Char(
        string="Account Number",
        required=True,
        readonly=True,
        index=True,
    )
    payment_method = fields.Selection(
        selection=[
            ('none', 'N/A'),
            ('visa', 'Visa'),
            ('master_card', "Master Card"),
            ('mashreq', "Mashreq")],
        string="Payment Method",
        readonly=True,
        required=True,
        default='none',
        index=True,
    )
    is_mada = fields.Boolean(
        string="Is MADA?",
        readonly=True,
        default=False,
    )
    transaction_date = fields.Date(
        string="Transaction Date",
        readonly=True,
        index=True,
    )
    card_number = fields.Char(
        string="Card Number",
        readonly=True,
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    gross_amount = fields.Monetary(
        string="Gross Transaction Amount",
        currency_field='currency_id',
        readonly=True,
    )
    net_transaction_amount = fields.Monetary(
        string="Net Transaction Amount",
        currency_field='currency_id',
        readonly=True,
    )
    merchant_charge_amount = fields.Monetary(
        string="Reported Merchant Charges",
        currency_field='currency_id',
        readonly=True,
    )
    merchant_charge_vat = fields.Monetary(
        string="Reported Merchant VAT",
        currency_field='currency_id',
        readonly=True,
    )
    # TODO: Correct type
    payment_status = fields.Selection(
        string="Payment Status",
        selection=[('capture', 'Capture'), ('refund', 'Refund')],
        required=True,
        readonly=True,
        index=True,
    )
    auth_code = fields.Char(
        string="Auth Code",
        required=True,
        readonly=True,
    )
    is_3d_secure = fields.Boolean(
        string="Is 3d Secure?",
        readonly=True,
        default=False
    )
    posting_date = fields.Date(
        string="Posting Date",
        readonly=True,
    )
    payment_gateway_id = fields.Many2one(
        string="Payment Gateway Id",
        comodel_name='ofh.payment.gateway',
        required=False,
        ondelete='cascade'
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
        track_visibility='always',
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
        store=True,
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
