from odoo import fields, models


class OfhPayment(models.Model):
    _inherit = 'ofh.payment'

    payment_gateway_ids = fields.One2many(
        string="Payment Gateway ID",
        comodel_name='ofh.payment.gateway',
        inverse_name='hub_payment_id',
    )

