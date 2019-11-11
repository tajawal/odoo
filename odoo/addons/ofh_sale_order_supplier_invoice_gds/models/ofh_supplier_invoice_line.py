# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models
from odoo.addons.queue_job.job import job


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    cost_amount = fields.Monetary(
        string="Supplier Cost",
        currency_field='currency_id',
        compute='_compute_cost_amount',
        readonly=True,
        store=False,
    )

    @api.multi
    @api.depends(
        'invoice_type', 'gds_net_amount', 'gds_alshamel_cost', 'total')
    def _compute_cost_amount(self):
        for rec in self:
            if rec.invoice_type == 'gds':
                rec.cost_amount = rec.gds_net_amount
                if 'KWD' in rec.office_id:
                    rec.cost_amount += rec.gds_alshamel_cost
            else:
                rec.cost_amount = rec.total

    @api.multi
    def _match_gds_with_sale_order(self):
        self.ensure_one()
        if self.invoice_type != 'gds':
            return

        order_ids = self.env['ofh.sale.order'].search(
            self._get_gds_sale_order_domain())

        if not order_ids:
            self.message_post(f"No match found.")
            return

        if len(order_ids) == 1:
            self.order_id = order_ids[0]
            return

        order_names = ', '.join([o.name for o in order_ids])
        self.message_post(
            f"Line matches with multiple Sale orders: {order_names}")
        return

    @api.multi
    def _match_gds_with_sale_order_line(self):
        # Refund an Amendments never matches with Initial Booking.
        self.ensure_one()
        if self.invoice_status in ('AMND', 'RFND'):
            return

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
    def _match_gds_with_payment_request(self):
        self.ensure_one()

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
    def _get_gds_sale_order_domain(self):
        self.ensure_one()

        if self.order_reference:
            return [('name', '=', self.order_reference)]

        return [
            ('order_type', '=', 'flight'),
            '|',
            ('supplier_reference', '=', self.locator.strip()),
            ('vendor_reference', '=', self.locator.strip())]

    @api.multi
    def action_gds_record_locator(self):
        lines = self.filtered(
            lambda l: l.invoice_type == 'gds'
            and l.matching_status == 'unmatched')
        return super(
            OfhSupplierInvoiceLine, lines).action_gds_record_locator()

    @job(default_channel='root.import')
    @api.multi
    def gds_retrieve_pnr(self):
        self.ensure_one()
        super(OfhSupplierInvoiceLine, self).gds_retrieve_pnr()
        if not self.order_reference:
            return

        tajawal_date = datetime.strptime(
            f'201{self.order_reference[1:6]}', '%Y%m%d')

        # A Ticket will be unusable after one year of the purchase.
        if (datetime.now() - tajawal_date).days > 363:
            self.write({
                'matching_status': 'unused_ticket',
                'reconciliation_status': 'not_applicable',
            })
        else:
            self.match_with_sale_order()
