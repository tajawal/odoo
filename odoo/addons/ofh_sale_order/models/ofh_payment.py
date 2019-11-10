from odoo import fields, models


class OfhPayment(models.Model):

    _inherit = 'ofh.payment'

    order_id = fields.Many2one(
        string="Order",
        required=True,
        readonly=True,
        index=True,
        comodel_name='ofh.sale.order',
        ondelete='cascade',
        auto_join=True,
    )
    ticketing_office_id = fields.Char(
        related="order_id.ticketing_office_id",
    )
