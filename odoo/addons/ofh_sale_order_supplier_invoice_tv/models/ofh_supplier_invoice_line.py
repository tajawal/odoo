# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class OfhSupplierInvoiceLine(models.Model):
    _inherit = 'ofh.supplier.invoice.line'

    @api.multi
    def _match_tv_with_sale_order(self):
        self.ensure_one()
        if self.invoice_type != 'tv':
            return

        order_ids = self.env['ofh.sale.order'].search(
            self._get_tv_sale_order_domain())

        if not order_ids:
            self.message_post("No match found.")
            return

        if len(order_ids) == 1:
            self.order_id = order_ids[0]
            return

        order_names = ', '.join([o.name for o in order_ids])
        self.message_post(
            f"Line matches with multiple Sale orders: {order_names}")
        return

    @api.multi
    def _match_tv_with_sale_order_line(self):
        self.ensure_one()

        from_str = fields.Date.from_string

        for line in self.order_id.line_ids:
            if line.matching_status in ('matched', 'not_applicable'):
                continue

            day_diff = abs((
                from_str(line.created_at) - from_str(self.invoice_date)).days)

            if day_diff > 2:
                continue

            if (line.line_reference and
                self.ticket_number in line.line_reference) or \
                    (line.manual_line_reference and
                     self.ticket_number in line.manual_line_reference):
                line.write({
                    'invoice_line_ids': [(4, self.id)],
                    'matching_status': 'matched',
                })
        return

    @api.multi
    def _match_tv_with_payment_request(self):
        pass

    @api.multi
    def _get_tv_sale_order_domain(self):
        self.ensure_one()

        if self.order_reference:
            return [('name', '=', self.order_reference)]

        return [
            ('vendor_reference', '=', self.locator.strip()),
            ('order_type', '=', 'hotel')]
