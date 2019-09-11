from odoo import fields, models


class OfhPaymentRequest(models.Model):

    _inherit = 'ofh.payment.request'

    payment_gateway_id = fields.Many2one(
        string="Payment Gateway ID",
        required=True,
        readonly=True,
        index=True,
        comodel_name='ofh.payment.gateway',
        ondelete='cascade',
        auto_join=True,
    )
