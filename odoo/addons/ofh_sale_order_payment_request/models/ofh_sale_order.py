# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class OfhSaleOrder(models.Model):

    _inherit = ['ofh.sale.order']

    payment_request_ids = fields.One2many(
        comodel_name="ofh.payment.request",
        string="Payment Request IDs",
        inverse_name='order_id',
        readonly=True,
    )
