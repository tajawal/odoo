# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OfhPaymentCharge(models.Model):
    _inherit = 'ofh.payment.charge'

    payment_id = fields.Many2one(
        comodel_name="ofh.payment",
        string="Payment ID",
        readonly=True,
        index=True,
        ondelete="cascade",
    )
