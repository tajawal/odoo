# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class OfhPaymentGateway(models.Model):
    _name = 'ofh.payment.gateway'
    _description = "Ofh Payment Gateway"

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
        compute='_compute_name',
        readonly=True,
        store=True,
    )
    payment_gateway_id = fields.Char(
        string="Payment Gateway ID",
        readonly=True,
        required=True,
        index=True,
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
    payment_method = fields.Char(
        string="Payment Method",
        required=True,
        readonly=True,
    )
    payment_by = fields.Char(
        string="Payment Method",
        required=True,
        readonly=True,
    )
    transaction_date = fields.Datetime(
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
            ('Void authorization', 'Void Authorisation'),
            ('Authorization', 'Authorisation'),
            ('Captured', 'Capture'),
            ('Capture', 'Capture')],
        required=False,
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
    card_type = fields.Char(
        string="Card Type",
        readonly=True,
    )
    card_wallet_type = fields.Char(
        string="Card Wallet Type",
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

    @api.multi
    @api.depends('provider', 'auth_code')
    def _compute_name(self):
        for rec in self:
            compute_function = '_{}_compute_name'.format(rec.provider)
            if hasattr(rec, compute_function):
                getattr(rec, compute_function)()
            else:
                rec.name = '{}{}'.format(rec.provider, rec.auth_code)


