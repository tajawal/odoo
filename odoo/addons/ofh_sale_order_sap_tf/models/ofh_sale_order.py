# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from odoo import api, models, fields


class OfhSaleOrder(models.Model):
    _inherit = 'ofh.sale.order'

    @api.multi
    def _prepare_sap_lines_values(self):
        """Override this method to handle the case where multiple GDS lines are
        fulfilled by TF. In this case the booking is no longer sent ticket wise
        but PNR wise (Most of the time one tf line should be sent).
        """
        self.ensure_one()

        backend = self.env['sap.backend'].search([], limit=1)

        # Usually the GDS booking lines are unmatched when they're fullfiled
        # within TF.
        if not all([
                l.reconciliation_status == 'not_applicable'
                for l in self.line_ids]):
            return super(OfhSaleOrder, self)._prepare_sap_lines_values()

        order_vendor = list(set(self.line_ids.mapped("vendor_name")))
        invoice_type = list(set(self.invoice_line_ids.mapped("invoice_type")))

        # We need to make sure that the order lines are gds and the invoice
        # lines are all tf. Not sure if the condition should be that strict but
        # it will reduce the risk of bugs with other cases.
        if len(order_vendor) == 1 and len(invoice_type) == 1 and \
                order_vendor[0] != invoice_type[0] and \
                invoice_type[0] == 'tf':

            sale_line_dict = self.line_ids[0]._get_sale_line_dict()
            sale_line_dict['pnr'] = self.invoice_line_ids[0].locator
            sale_line_dict['cost_currency'] = \
                self.invoice_line_ids[0].currency_id.name
            sale_line_dict['cost_price'] = sum([
                l.total for l in self.invoice_line_ids])
            sale_line_dict['sale_price'] = sum(
                [l.sale_price for l in self.line_ids])
            sale_line_dict['discount'] = sum(
                [l.discount_amount for l in self.line_ids])
            sale_line_dict['ticket_number'] = ''
            sale_line_dict['output_vat'] = sum(
                [l.tax_amount for l in self.line_ids])
            sale_line_dict['vendor_name'] = 'tf'

            return [(0, 0, {
                'send_date': fields.Datetime.now(),
                'backend_id': backend.id,
                'sale_order_line_id': self.line_ids[0].id,
                'line_detail': json.dumps(sale_line_dict)})]

        return super(OfhSaleOrder, self)._prepare_sap_lines_values()
