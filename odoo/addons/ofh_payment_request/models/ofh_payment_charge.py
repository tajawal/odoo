# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OfhPaymentCharge(models.Model):
    _inherit = 'ofh.payment.charge'

    payment_request_id = fields.Many2one(
        comodel_name="ofh.payment.request",
        string="Payment Request ID",
        readonly=True,
        ondelete="cascade",
        index=True,
    )
