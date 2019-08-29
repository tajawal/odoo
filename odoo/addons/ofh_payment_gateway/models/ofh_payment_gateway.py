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
        selection=[],
        required=True,
        readonly=True,
        index=True,
        compute="_compute_payment_gateway",
        store=False
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
        compute="_compute_payment_gateway",
        store=False
    )
    track_id = fields.Char(
        string="Track ID",
        required=True,
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    auth_code = fields.Char(
        string="Auth Code",
        required=True,
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    # TODO should be selection list?
    payment_method = fields.Char(
        string="Payment Method",
        required=True,
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
    )
    payment_by = fields.Selection(
        string="Payment By",
        selection=[
            ('credit_card', 'Credit Card'),
        ],
        required=True,
        readonly=True,
        default='credit_card',
        compute="_compute_payment_gateway",
        store=False
    )
    transaction_date = fields.Datetime(
        string="Transaction Date",
        required=True,
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
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
        required=True,
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
        required=True,
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
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
        store=False
    )
    is_apple_pay = fields.Boolean(
        string="Apple Pay?",
        default=False,
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
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
        store=False
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
        store=False
    )
    payment_id = fields.Char(
        string="Payment ID",
        readonly=True,
        compute="_compute_payment_gateway",
        store=False
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
        store=False
    )
    is_3d_secure = fields.Boolean(
        string="Is 3d Secure?",
        readonly=True,
        default=False,
        compute="_compute_payment_gateway",
        store=False
    )
    payment_gateway_line_ids = fields.One2many(
        string="Payment Gateway Lines",
        comodel_name='ofh.payment.gateway.line',
        inverse_name='payment_gateway_id',
    )

    _sql_constraints = [
        ('unique_payment_getway', 'unique(name)',
         _("This line has been uploaded"))
    ]

    @api.multi
    @api.depends('payment_gateway_line_ids')
    def _compute_payment_gateway(self):
        for rec in self:
            if not rec.payment_gateway_line_ids:
                continue
            self.provider = rec.payment_gateway_line_ids[0].provider
            self.acquirer_bank = rec.payment_gateway_line_ids[0].acquirer_bank
            self.track_id = rec.payment_gateway_line_ids[0].track_id
            self.auth_code = rec.payment_gateway_line_ids[0].auth_code
            self.payment_method = rec.payment_gateway_line_ids[0].payment_method
            self.payment_by = rec.payment_gateway_line_ids[0].payment_by
            self.transaction_date = rec.payment_gateway_line_ids[0].transaction_date
            self.total = rec.payment_gateway_line_ids[0].total
            self.currency_id = rec.payment_gateway_line_ids[0].currency_id
            self.payment_status = rec.payment_gateway_line_ids[0].payment_status
            self.card_name = rec.payment_gateway_line_ids[0].card_name
            self.card_number = rec.payment_gateway_line_ids[0].card_number
            self.card_bin = rec.payment_gateway_line_ids[0].card_bin
            self.card_bank = rec.payment_gateway_line_ids[0].card_bank
            self.is_card_mada = rec.payment_gateway_line_ids[0].is_card_mada
            self.is_apple_pay = rec.payment_gateway_line_ids[0].is_apple_pay
            self.card_expiry_year = rec.payment_gateway_line_ids[0].card_expiry_year
            self.card_expiry_month = rec.payment_gateway_line_ids[0].card_expiry_month
            self.response_description = rec.payment_gateway_line_ids[0].response_description
            self.customer_email = rec.payment_gateway_line_ids[0].customer_email
            self.cvv_check = rec.payment_gateway_line_ids[0].cvv_check
            self.arn = rec.payment_gateway_line_ids[0].arn
            self.payment_id = rec.payment_gateway_line_ids[0].payment_id
            self.server_ip = rec.payment_gateway_line_ids[0].server_ip
            self.reported_mid = rec.payment_gateway_line_ids[0].reported_mid
            self.is_3d_secure = rec.payment_gateway_line_ids[0].is_3d_secure
