# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OfhBankSettlement(models.Model):
    _inherit = 'ofh.bank.settlement'

    bank_name = fields.Selection(
        selection_add=[('rajhi', 'Rajhi')],
    )
