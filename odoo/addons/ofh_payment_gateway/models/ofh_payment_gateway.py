# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class OfhPaymentGateway(models.Model):
    _name = 'ofh.payment.gateway'
    _description = "Ofh Payment Gateway"

    name = fields.Char(
        string="Payment Reference",
        readonly=True,
        index=True,
        required=True,
    )
    provider = fields.Selection(
        string="Provider",
        selection=[
            ('checkout', 'Checkout'),
            ('fort', 'Fort'),
            ('knet', 'Knet'),
        ],
        readonly=True,
        index=True,
        compute="_compute_payment_gateway",
        store=True
    )
    acquirer_bank = fields.Selection(
        string="Acquirer Bank",
        selection=[
            ('mashreq', 'Mashreq'),
            ('cib', 'CIB'),
            ('sabb', 'SABB'),
            ('rajhi', 'Rajhi'),
            ('knet', 'Knet'),
            ('amex', 'Amex')],
        readonly=True,
        compute="_compute_payment_gateway",
        store=True
    )
    track_id = fields.Char(
        string="Track ID",
        readonly=True,
        compute="_compute_payment_gateway",
        store=True,
        index=True,
    )
    auth_code = fields.Char(
        string="Auth Code",
        readonly=True,
        compute="_compute_payment_gateway",
        store=True
    )
    # TODO should be selection list?
    payment_method = fields.Char(
        string="Payment Method",
        readonly=True,
        compute="_compute_payment_gateway",
        store=True
    )
    payment_by = fields.Selection(
        string="Payment By",
        selection=[
            ('credit_card', 'Credit Card'),
        ],
        readonly=True,
        default='credit_card',
        compute="_compute_payment_gateway",
        store=False
    )
    transaction_date = fields.Datetime(
        string="Transaction Date",
        readonly=True,
        compute="_compute_payment_gateway",
        store=True
    )
    total = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    payment_status = fields.Selection(
        string="Payment Status",
        selection=[
            ('void', 'Voided'),
            ('auth', 'Authorised'),
            ('capture', 'Captured'),
            ('refund', 'Refunded')],
        readonly=True,
        compute="_compute_payment_gateway",
        store=True
    )
    card_name = fields.Char(
        string="Card Name",
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    card_number = fields.Char(
        string="Card Number",
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    card_bin = fields.Char(
        string="Card Bin",
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    card_bank = fields.Char(
        string="Card Issuing Bank",
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    is_card_mada = fields.Boolean(
        string="MADA?",
        readonly=True,
        default=False,
        compute="_compute_payment_gateway",
        store=True
    )
    is_apple_pay = fields.Boolean(
        string="Apple Pay?",
        default=False,
        readonly=True,
        compute="_compute_payment_gateway",
        store=True
    )
    card_expiry_year = fields.Char(
        string="Card Expiry Year",
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    card_expiry_month = fields.Char(
        string="Card Expiry Month",
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    response_description = fields.Char(
        string="Response Description",
        readonly=True,
        compute="_compute_payment_gateway",
        store=True
    )
    customer_email = fields.Char(
        string="Customer Email",
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    cvv_check = fields.Char(
        string="CVV Check",
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    arn = fields.Char(
        string="ARN",
        readonly=True,
        compute="_compute_payment_gateway",
        store=True
    )
    payment_id = fields.Char(
        string="Payment ID",
        readonly=True,
        compute="_compute_payment_gateway",
        store=True
    )
    server_ip = fields.Char(
        string="Server IP",
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    reported_mid = fields.Char(
        string="Reported MID",
        readonly=True,
        compute="_compute_payment_gateway",
        store=True
    )
    is_3d_secure = fields.Boolean(
        string="Is 3d Secure?",
        readonly=True,
        default=False,
        compute="_compute_payment_gateway",
        store=True
    )
    entity = fields.Selection(
        selection=[
            ('almosafer', 'Almosafer'),
            ('tajawal', 'Tajawal')],
        readonly=True,
        default="almosafer",
        index=True,
        compute="_compute_payment_gateway",
        store=True
    )
    payment_gateway_line_ids = fields.One2many(
        string="Payment Gateway Lines",
        comodel_name='ofh.payment.gateway.line',
        inverse_name='payment_gateway_id',
    )

    _sql_constraints = [
        ('unique_payment_getway', 'unique(name, payment_status)',
         _("This line has been uploaded"))
    ]

    @api.multi
    @api.depends('payment_gateway_line_ids')
    def _compute_payment_gateway(self):
        for rec in self:
            if not rec.payment_gateway_line_ids:
                continue

            pg_line = rec.payment_gateway_line_ids.filtered(
                lambda rec: rec.payment_status and rec.payment_status == 'capture')

            if pg_line:
                pg_line = pg_line[0]
            else:
                pg_line = rec.payment_gateway_line_ids[0]

            rec.provider = pg_line.provider
            rec.acquirer_bank = pg_line.acquirer_bank
            rec.track_id = pg_line.track_id
            rec.auth_code = pg_line.auth_code
            rec.payment_method = pg_line.payment_method
            rec.payment_by = pg_line.payment_by
            rec.transaction_date = \
                pg_line.transaction_date
            rec.total = pg_line.total
            rec.currency_id = pg_line.currency_id
            rec.payment_status = pg_line.payment_status
            rec.card_name = pg_line.card_name
            rec.card_number = pg_line.card_number
            rec.card_bin = pg_line.card_bin
            rec.card_bank = pg_line.card_bank
            rec.is_card_mada = pg_line.is_card_mada
            rec.is_apple_pay = pg_line.is_apple_pay
            rec.card_expiry_year = \
                pg_line.card_expiry_year
            rec.card_expiry_month = \
                pg_line.card_expiry_month
            rec.response_description = \
                pg_line.response_description
            rec.customer_email = pg_line.customer_email
            rec.cvv_check = pg_line.cvv_check
            rec.arn = pg_line.arn
            rec.payment_id = pg_line.payment_id
            rec.server_ip = pg_line.server_ip
            rec.reported_mid = pg_line.reported_mid
            rec.is_3d_secure = pg_line.is_3d_secure
            rec.entity = pg_line.entity

            pg_line = rec.payment_gateway_line_ids.filtered(
                lambda rec: rec.auth_code and rec.auth_code != '000000')
            if pg_line:
                rec.auth_code = pg_line[0].auth_code

            # Pick arn from the Authorised one
            pg_line = rec.payment_gateway_line_ids.filtered(
                lambda rec: rec.arn)
            if pg_line:
                rec.arn = pg_line[0].arn
