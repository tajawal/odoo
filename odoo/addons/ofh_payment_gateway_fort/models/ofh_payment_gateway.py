# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class OfhPaymentGateway(models.Model):
    _inherit = 'ofh.payment.gateway'

    provider = fields.Selection(
        selection_add=[('fort', 'Fort')],
    )

    @api.multi
    def _fort_compute_name(self):
        self.ensure_one
        self.name = '{}_{}'.format(
            self.provider, self.auth_code)



