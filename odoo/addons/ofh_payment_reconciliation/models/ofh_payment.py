from odoo import fields, models, api


class OfhPayment(models.Model):
    _inherit = 'ofh.payment'

    payment_gateway_ids = fields.One2many(
        string="Payment Gateway ID",
        comodel_name='ofh.payment.gateway',
        inverse_name='hub_payment_id',
    )
    bank_settlement_ids = fields.One2many(
        string="Bank Settlements",
        related="payment_gateway_ids.bank_settlement_ids",
        readonly=True,
        store=False,
    )
    settlement_date = fields.Date(
        string="Bank Settlement Date",
        related="bank_settlement_ids.settlement_date",
    )


