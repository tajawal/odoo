# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

BOOKING_CAT_INIT = 'initial'
BOOKING_CAT_AMND = 'amendment'


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    @api.multi
    def _match_tf_with_sale_order(self):
        if self.invoice_type != 'tf':
            return

        order_ids = self.env['ofh.sale.order'].search(
            self._get_tf_sale_order_domain())

        initial_orders = order_ids.filtered(
            lambda p: p.booking_category == BOOKING_CAT_INIT)

        amendment_orders = order_ids.filtered(
            lambda p: p.booking_category == BOOKING_CAT_AMND)

        # Matching with Initial Orders
        if len(initial_orders) == 1:
            self.order_id = initial_orders[0]
            self._match_tf_with_sale_order_line()
            return

        # Matching with Amendment Orders
        if amendment_orders:
            for a_order in amendment_orders:
                self.order_id = a_order
                self._match_tf_with_sale_order_line()
            return

        order_names = ', '.join([o.name for o in order_ids])
        self.message_post(
            f"Line matches with multiple Sale orders: {order_names}")
        return

    @api.multi
    def _match_tf_with_sale_order_line(self):
        # Refund an Amendments never matches with Initial Booking.
        self.ensure_one()
        if self.invoice_status in ('RFND'):
            return

        # Match initial with only TKTT
        if self.order_id.booking_category == BOOKING_CAT_INIT and \
                self.invoice_status != 'TKTT':
            return

        # Match amendment with only AMND
        if self.order_id.booking_category == BOOKING_CAT_AMND and \
                self.invoice_status != 'AMND':
            return

        from_str = fields.Date.from_string

        for line in self.order_id.line_ids:
            day_diff = abs((
                from_str(line.created_at) -
                from_str(self.invoice_date)).days)
            if day_diff > 2:
                return

            # Adding amount check in case of Amendment
            if self.order_id.booking_category == BOOKING_CAT_AMND:
                total_supplier_cost = self.order_id.total_supplier_cost

                supplier_cost = sum([
                    l.cost_amount for l in self.order_id.invoice_line_ids])
                supplier_cost += self.cost_amount

                diff = abs(
                    supplier_cost /
                    total_supplier_cost)
                if diff > 1.35:
                    continue

            line.write({
                'invoice_line_ids': [(4, self.id)],
                'matching_status': 'matched',
            })

        return

    @api.multi
    def _match_tf_with_payment_request(self):
        self.ensure_one()

        # Continue only in case of Refund
        if self.invoice_status in ('TKTT', 'AMND'):
            return

        # If the current line has already matched with an initial ticket
        if not self.order_id or self.order_line_id:
            return

        # If the order doesn't have any payment requests.
        if not self.order_id.payment_request_ids:
            return

        from_str = fields.Date.from_string

        for payment_request in self.order_id.payment_request_ids:
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
                l.cost_amount for l in payment_request.supplier_invoice_ids])
            supplier_cost += self.cost_amount

            diff = abs(
                supplier_cost /
                payment_request.estimated_cost_in_supplier_currency)

            if diff > 1.35:
                continue

            payment_request.write({
                'supplier_invoice_ids': [(4, self.id)],
                'matching_status': 'matched',
            })
        return

    @api.multi
    def _get_tf_sale_order_domain(self):
        self.ensure_one()
        # TODO: we've issue of module dependency here, I should takeout the
        # GDS office IDs
        office_ids = self.env['ofh.gds.office'].search([])
        offices = [o.name for o in office_ids]
        return [
            ('order_type', '=', 'flight'),
            ('ticketing_office_id', 'not in', offices),
            '|',
            ('supplier_reference', '=', self.locator.strip()),
            ('vendor_reference', '=', self.locator.strip())]
