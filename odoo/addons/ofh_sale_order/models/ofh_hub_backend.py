# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class HubBackend(models.Model):

    _inherit = 'hub.backend'

    import_sale_order_from_date = fields.Datetime(
        string="Import Sale order from date",
        readonly=True,
    )

    @api.multi
    def import_payment_requests(self):
        self.ensure_one()
        backend = self.search([], limit=1)
        backend._import_from_date(
            'hub.sale.order', 'import_sale_order_from_date')
        return True
