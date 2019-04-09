# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HubPaymentCharge(models.Model):
    _name = 'hub.payment.charge'
    _inherit = 'hub.binding'
    _inherits = {'ofh.payment.charge': 'odoo_id'}

    odoo_id = fields.Many2one(
        comodel_name='ofh.payment.charge',
        string='Order',
        required=True,
        ondelete='cascade',
    )
