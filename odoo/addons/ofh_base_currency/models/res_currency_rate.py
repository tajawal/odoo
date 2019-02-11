# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCurrencyRate(models.Model):

    _inherit = 'res.currency.rate'

    currency_id = fields.Many2one(
        readonly=False,
        required=True,
    )
