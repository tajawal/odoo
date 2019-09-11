from odoo import fields, models


class OfhPayment(models.Model):
    _inherit = 'ofh.payment'

    payment_gateway_id = fields.Many2one(
        string="Payment Gateway ID",
        required=False,
        readonly=True,
        index=True,
        comodel_name='ofh.payment.gateway',
        ondelete='cascade',
        auto_join=True,
    )