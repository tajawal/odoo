# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import json


class OfhPayment(models.Model):
    _inherit = 'ofh.payment.sap'

    sap_payment_ids = fields.One2many(
        string="Sap Payment Ids",
        comodel_name="ofh.payment.sap",
        inverse_name='sap_sale_order_id',
        readonly=True,
    )
