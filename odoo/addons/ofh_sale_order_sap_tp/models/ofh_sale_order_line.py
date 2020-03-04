# Copyright 2020 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class OfhSaleOrderLine(models.Model):

    _inherit = 'ofh.sale.order.line'

    @api.multi
    def _get_tp_sale_line_dict(self):
        self.ensure_one()
        lines = []

        total_cost = sum([l.gds_net_amount for l in self.invoice_line_ids])
        for line in self.invoice_line_ids:
            line_dict = self._get_sale_line_dict()
            line_dict['pnr'] = line.locator
            line_dict['cost_price'] = abs(line.currency_id.round(
                line.gds_net_amount))

            prorated_sale = \
                (line.gds_net_amount * self.total_amount) / total_cost
            line_dict['sale_price'] = abs(
                line.currency_id.round(prorated_sale))

            prorated_discount = \
                (line.gds_net_amount * self.discount_amount) / total_cost
            line_dict['discount'] = abs(
                line.currency_id.round(prorated_discount))

            prorated_tax = \
                (line.gds_net_amount * self.tax_amount) / total_cost
            line_dict['output_vat'] = abs(line.currency_id.round(prorated_tax))

            line_dict['cost_currency'] = line.currency_id.name
            line_dict['ticket_number'] = line.ticket_number[-10:]
            line_dict['office_id'] = line.office_id
            lines.append(line_dict)
        return lines
