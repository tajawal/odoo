# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OfhBankSettlement(models.Model):
    _name = 'ofh.bank.settlement'
    _description = "Ofh Bank Settlement"
    _rec_name = 'name'

    created_at = fields.Datetime(
        required=True,
        readonly=True,
    )
    updated_at = fields.Datetime(
        required=True,
        readonly=True,
        track_visibility='always',
    )
    name = fields.Char(
        string="Name",
        readonly=True,
        required=True,
        index=True,
    )
    bank_name = fields.Selection(
        string="Bank Name",
        selection=[
            ('sabb', 'SABB'),
            ('rajhi', 'Rajhi'),
            ('mashreq', 'Mashreq'),
            ('amex', 'Amex')],
        required=True,
        readonly=True,
        index=True,
    )
    reported_mid = fields.Char(
        string="Reported MID",
        required=True,
        readonly=True,
        index=True,
    )
    account_number = fields.Char(
        string="Account Number",
        required=True,
        readonly=True,
        index=True,
    )
    payment_method = fields.Char(
        string="Payment Method",
        readonly=True,
    )
    card_type = fields.Char(
        string="Card Type",
        readonly=True,
    )
    transaction_date = fields.Datetime(
        string="Transaction Date",
        required=True,
        readonly=True,
    )
    card_number = fields.Char(
        string="Card Number",
        readonly=True,
    )
    gross_transaction_amount = fields.Monetary(
        string="Gross Transaction Amount",
        currency_field='currency_id',
        readonly=True,
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    reported_merchant_charges = fields.Monetary(
        string="Reported Merchant Charges",
        currency_field='currency_id',
        readonly=True,
    )
    reported_merchant_vat = fields.Monetary(
        string="Reported Merchant VAT",
        currency_field='currency_id',
        readonly=True,
    )
    # TODO: Correct type
    payment_status = fields.Char(
        string="Payment Status",
        required=False,
        readonly=True,
    )
    arn = fields.Char(
        string="ARN",
        readonly=True,
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
    net_transaction_amount = fields.Monetary(
        string="Net Transaction Amount",
        currency_field='currency_id',
        readonly=True,
    )
    posting_date = fields.Datetime(
        string="Posting Date",
        readonly=True,
    )
    reconciliation_reference_id = fields.Char(
        string="Reconciliation Reference ID",
        readonly=True,
    )
    full_terminal_number = fields.Char(
        string="Full Terminal Number",
        readonly=True,
    )
    settlement_date = fields.Datetime(
        string="Settlement Date",
        readonly=True,
    )





