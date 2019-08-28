# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OfhBankSettlement(models.Model):
    _name = 'ofh.bank.settlement'
    _description = "Bank Settlement"
    _rec_name = 'name'

    name = fields.Char(
        string="ARN",
        readonly=True,
        required=True,
    )
    settlement_date = fields.Datetime(
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
            ('visa', 'VISA'),
            ('master_card', "Master Card")],
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
    transaction_date = fields.Datetime(
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
    posting_date = fields.Datetime(
        string="Posting Date",
        readonly=True,
    )
