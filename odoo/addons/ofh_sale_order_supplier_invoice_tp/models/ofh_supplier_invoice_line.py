# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models
from odoo.addons.queue_job.job import job

BOOKING_CAT_INIT = 'initial'
BOOKING_CAT_AMND = 'amendment'


class OfhSupplierInvoiceLine(models.Model):
    _inherit = 'ofh.supplier.invoice.line'

    @api.multi
    def _match_tp_with_sale_order(self):
        self.ensure_one()
        if self.invoice_type != 'tp':
            return

        order_ids = self.env['ofh.sale.order'].search(
            self._get_tp_sale_order_domain())

        if not order_ids:
            self.message_post(f"No match found.")
            return

        initial_orders = order_ids.filtered(
            lambda p: p.booking_category == BOOKING_CAT_INIT)

        if len(initial_orders) > 1:
            order_names = ', '.join([o.name for o in order_ids])
            self.message_post(
                f"Line matches with multiple Sale orders: {order_names}")
            return

        # Matching with Initial Orders
        self._match_tp_with_sale_order_line(initial_orders)
        if self.order_id:
            return

        # Matching with Amendment Orders
        amendment_orders = order_ids.filtered(
            lambda p: p.booking_category == BOOKING_CAT_AMND)

        if not amendment_orders:
            return

        for a_order in amendment_orders:
            self._match_tp_with_sale_order_line(a_order)
            if self.order_id:
                return

        return

    @api.multi
    def _match_tp_with_sale_order_line(self, order_id):
        # Refund an Amendments never matches with Initial Booking.
        self.ensure_one()
        if self.invoice_status == 'RFND':
            self._match_tp_with_payment_request(order_id)
            return

        from_str = fields.Date.from_string

        for line in order_id.line_ids:
            match = False
            if order_id.booking_category == BOOKING_CAT_INIT and \
                    line.matching_status in ('matched', 'not_applicable'):
                continue

            day_diff = abs((from_str(line.created_at) - from_str(self.invoice_date)).days)

            if day_diff > 2:
                continue

            if (line.line_reference and
                self.ticket_number in line.line_reference) or \
                    (line.manual_line_reference and
                     self.ticket_number in line.manual_line_reference):
                match = True

            # Adding amount check in case of Amendment
            if order_id.booking_category == BOOKING_CAT_AMND and \
                    self.order_id.store_id != '1000' and not match:
                total_supplier_cost = order_id.total_supplier_cost

                supplier_cost = sum([
                    l.total for l in order_id.invoice_line_ids])
                supplier_cost += self.total

                diff = abs(
                    supplier_cost /
                    total_supplier_cost)
                if diff > 1.35:
                    continue
                else:
                    match = True

            if match:
                self.order_id = order_id
                line.write({
                    'invoice_line_ids': [(4, self.id)],
                    'matching_status': 'matched',
                })
        return

    @api.multi
    def _match_tp_with_payment_request(self, order_id):
        self.ensure_one()

        # Continue only in case of Refund
        if self.invoice_status in ('TKTT', 'AMND'):
            return

        # If the current line has already matched with an initial ticket
        if not order_id or self.order_line_id:
            return

        # If the order doesn't have any payment requests.
        if not order_id.payment_request_ids:
            return

        from_str = fields.Date.from_string

        for payment_request in order_id.payment_request_ids:
            day_diff = abs((
                                   from_str(payment_request.updated_at) -
                                   from_str(self.invoice_date)).days)

            if day_diff > 2:
                continue

            pr_type = 'charge' if self.invoice_status in ('TKTT', 'AMND') \
                else 'refund'

            # Match only supplier lines and payment request of the same type.
            if payment_request.request_type != pr_type:
                continue

            supplier_cost = sum([
                l.total for l in payment_request.supplier_invoice_ids])
            supplier_cost += self.total

            diff = abs(
                supplier_cost /
                payment_request.estimated_cost_in_supplier_currency)
            if diff > 1.35:
                continue

            self.order_id = order_id
            payment_request.write({
                'supplier_invoice_ids': [(4, self.id)],
                'matching_status': 'matched',
            })

            if self.payment_request_id:
                break

        return

    @api.multi
    def _get_tp_sale_order_domain(self):
        self.ensure_one()

        if self.order_reference:
            return [('name', '=', self.order_reference)]

        return [
            ('order_type', '=', 'flight'),
            '|',
            ('supplier_reference', '=', self.locator.strip()),
            ('vendor_reference', '=', self.locator.strip())]

