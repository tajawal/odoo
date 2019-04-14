# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.queue_job.job import job


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    order_id = fields.Many2one(
        string='Order',
        comodel_name='ofh.sale.order',
        track_visibility='always',
    )
    order_line_id = fields.Many2one(
        string='Order Line',
        comodel_name='ofh.sale.order.line',
        track_visibility='always',
        inverse='_update_matching_status',
    )
    payment_request_id = fields.Many2one(
        inverse='_update_matching_status',
    )
    matching_status = fields.Selection(
        string="Matching Status",
        selection=[
            ('order_matched', 'Matched With Initial Booking'),
            ('pr_matched', 'Matched with Payment Request'),
            ('unmatched', 'Unmatched'),
            ('unused_ticket', 'Unused Ticket'),
            ('adm', 'Debit Memo'),
        ],
        required=True,
        default='unmatched',
        index=True,
        readonly=True,
        track_visibility='always',
    )
    reconciliation_status = fields.Selection(
        string="Reconciliation status",
        selection=[
            ('reconciled', 'Reconciled'),
            ('unreconciled', 'Unreconciled'),
            ('not_applicable', 'Not Applicable'),
        ],
        default='unreconciled',
        required=True,
        index=True,
        readonly=True,
        track_visibility='always',
    )
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
            if rec.invoice_type == 'GDS':
                rec.cost_amount = rec.gds_net_amount
                if 'KWD' in rec.office_id:
                    rec.cost_amount += rec.gds_alshamel_cost
            else:
                rec.cost_amount = rec.total

    @api.multi
    def _update_matching_status(self):
        for rec in self:
            if rec.matching_status in ('unused_ticket', 'adm'):
                continue
            if rec.order_line_id:
                rec.matching_status = 'order_matched'
            elif rec.payment_request_id:
                rec.matching_status = 'pr_matched'
            else:
                rec.matching_status = 'unmatched'

    @api.multi
    @job(default_channel='root')
    def match_with_sale_order(self):
        """Match an invoice line with an order."""
        self.ensure_one()
        self._match_with_sale_order()
        self._match_with_sale_order_line()
        self._match_with_payment_request()

    @api.multi
    def _get_sale_order_domain(self):
        self.ensure_one()

        domain = []

        if self.invoice_type == 'tf':
            domain.append(('ticketing_office_id', '=', 'TRAVEL FUSION'))

        # TODO 1 year difference.
        domain.extend([
            '|',
            ('supplier_reference', 'like', self.locator),
            ('vendor_reference', 'like', self.locator)])

        return domain

    @api.multi
    def _match_with_sale_order(self):
        self.ensure_one()
        order_ids = self.env['ofh.sale.order'].search(
            self._get_sale_order_domain())

        if len(order_ids) == 1:
            self.order_id = order_ids[0]
            return

        if self.env.context.get('retrive_pnr'):
            # TODO retrieve PNR from command cryptic and match with
            # Reference
            pass
        else:
            return

    @api.multi
    def _match_with_sale_order_line(self):
        self.ensure_one()
        if not self.order_id:
            return
        for line in self.order_id.line_ids:
            if line.line_type == 'flight':
                self._match_with_flight_sale_order_line(line)
            elif line.line_type == 'hotel':
                # TODO matching logic for hotel invoice lines
                pass

    @api.multi
    def _match_with_flight_sale_order_line(self, line):
        from_str = fields.Date.from_string

        # Refund an Amendments never matches with Initial Booking.
        if self.invoice_status in ('AMND', 'RFND'):
            return

        # GDS matches with the ticket number.
        if self.invoice_type == 'gds':
            if self.ticket_number in line.line_reference:
                line.write({
                    'invoice_line_ids': [(4, self.id)],
                    'matching_status': 'matched',
                })

        # Travel Fusion matching is based on dates.
        elif self.invoice_type == 'tf':
            day_diff = abs((
                from_str(line.created_at) -
                from_str(self.invoice_date)).days)
            if day_diff > 2:
                return
            line.write({
                'invoice_line_ids': [(4, self.id)],
                'matching_status': 'matched',
            })

        return

    @api.multi
    def _match_with_payment_request(self):
        self.ensure_one

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
                'reconciliation_status': 'matched',
            })
            return
        return

    @api.model
    def _get_pending_invoice_lines(self, min_date=''):
        """Return invoice lines record set that hasn't matched yet
        :param min_date: minimum invoice line date to start a search from.
        :param min_date: str, optional
        :return: ofh.supplier.invoice.line record set
        :rtype: ofh.supplier.invoice.line()
        """
        domain = [('state', 'in', ('ready', 'investigate'))]
        if min_date:
            domain.append(('invoice_date', '>=', min_date))
        return self.search(domain)

    @api.model
    @job(default_channel='root')
    def match_supplier_invoice_lines(self):
        invoice_lines = self._get_pending_invoice_lines()
        for line in invoice_lines:
            line.with_delay().match_with_sale_order()

    @api.multi
    def action_unused_tickets_invoice_lines(self):
        lines = self.filtered(
            lambda l: l.invoice_type in ('gds', 'tf', 'galileo'))
        if not lines:
            return

        return lines.write({
            'order_id': False,
            'order_line_id': False,
            'payment_request_id': False,
            'matching_status': 'unused_ticket',
            'reconciliation_status': 'not_applicable',
        })
