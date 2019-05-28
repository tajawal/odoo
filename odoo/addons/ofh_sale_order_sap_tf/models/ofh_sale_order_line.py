# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class OfhSaleOrderLine(models.Model):

    _inherit = 'ofh.sale.order.line'

    @api.multi
    def _get_tf_sale_line_dict(self):
        self.ensure_one()
        sale_line_dict = self._get_sale_line_dict()

        sale_line_dict['pnr'] = self.invoice_line_ids[0].locator
        sale_line_dict['cost_price'] = sum([
            l.total for l in self.invoice_line_ids])
        sale_line_dict['cost_currency'] = \
            self.invoice_line_ids[0].currency_id.name
        sale_line_dict['ticket_number'] = ''

        return [sale_line_dict]
