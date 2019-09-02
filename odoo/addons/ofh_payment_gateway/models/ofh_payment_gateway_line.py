# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _


class OfhPaymentGatewayLine(models.Model):
    _name = 'ofh.payment.gateway.line'
    _description = "Ofh Payment Gateway Line"
    _order = 'transaction_date DESC'

    name = fields.Char(
        string="Payment Reference",
        readonly=True,
        index=True,
        required=True,
    )
    provider = fields.Selection(
        string="Provider",
        selection=[],
        required=True,
        readonly=True,
        index=True,
    )
    acquirer_bank = fields.Selection(
        string="Acquirer Bank",
        selection=[
            ('mashreq', 'Mashreq'),
            ('cib', 'CIB'),
            ('sabb', 'SABB'),
            ('rajhi', 'Rajhi'),
            ('knet', 'Knet')],
        required=True,
        readonly=True,
    )
    track_id = fields.Char(
        string="Track ID",
        required=True,
        readonly=True,
    )
    auth_code = fields.Char(
        string="Auth Code",
        required=True,
        readonly=True,
    )
    # TODO should be selection list?
    payment_method = fields.Char(
        string="Payment Method",
        required=True,
        readonly=True,
    )
    payment_by = fields.Selection(
        string="Payment By",
        selection=[
            ('credit_card', 'Credit Card'),
        ],
        required=True,
        readonly=True,
        default='credit_card',
    )
    transaction_date = fields.Datetime(
        string="Transaction Date",
        required=True,
        readonly=True,
    )
    total = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        readonly=True,
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    payment_status = fields.Selection(
        string="Payment Status",
        selection=[
            ('void', 'Voided'),
            ('auth', 'Authorised'),
            ('capture', 'Captured'),
            ('refund', 'Refunded')],
        required=True,
        readonly=True,
    )
    card_name = fields.Char(
        string="Card Name",
        readonly=True,
    )
    card_number = fields.Char(
        string="Card Number",
        readonly=True,
    )
    card_bin = fields.Char(
        string="Card Bin",
        readonly=True,
    )
    card_bank = fields.Char(
        string="Card Issuing Bank",
        readonly=True,
    )
    is_card_mada = fields.Boolean(
        string="MADA?",
        readonly=True,
        default=False,
    )
    is_apple_pay = fields.Boolean(
        string="Apple Pay?",
        default=False,
        readonly=True,
    )
    card_expiry_year = fields.Char(
        string="Card Expiry Year",
        readonly=True,
    )
    card_expiry_month = fields.Char(
        string="Card Expiry Month",
        readonly=True,
    )
    response_description = fields.Char(
        string="Response Description",
        readonly=True,
    )
    customer_email = fields.Char(
        string="Customer Email",
        readonly=True,
    )
    cvv_check = fields.Char(
        string="CVV Check",
        readonly=True,
    )
    arn = fields.Char(
        string="ARN",
        readonly=True,
    )
    payment_id = fields.Char(
        string="Payment ID",
        readonly=True,
        store=True
    )
    server_ip = fields.Char(
        string="Server IP",
        readonly=True,
    )
    reported_mid = fields.Char(
        string="Reported MID",
        readonly=True,
    )
    is_3d_secure = fields.Boolean(
        string="Is 3d Secure?",
        readonly=True,
        default=False
    )
    payment_gateway_id = fields.Many2one(
        string="Payment Gateway",
        required=True,
        readonly=True,
        index=True,
        comodel_name='ofh.payment.gateway',
        ondelete='cascade',
        auto_join=True,
    )

    _sql_constraints = [
        ('unique_payment_getway_line', 'unique(name)',
         _("This line has been uploaded"))
    ]
