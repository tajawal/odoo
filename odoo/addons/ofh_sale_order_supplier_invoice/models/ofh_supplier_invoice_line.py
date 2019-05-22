# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.addons.queue_job.job import job
from odoo.exceptions import MissingError, ValidationError


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    order_id = fields.Many2one(
        string='Order',
        comodel_name='ofh.sale.order',
        track_visibility='always',
        readonly=True,
    )
    order_line_id = fields.Many2one(
        string='Order Line',
        comodel_name='ofh.sale.order.line',
        track_visibility='always',
        inverse='_update_matching_status',
        readonly=True,
    )
    payment_request_id = fields.Many2one(
        inverse='_update_matching_status',
        readonly=True,
    )
    matching_status = fields.Selection(
        string="Matching Status",
        selection=[
            ('order_matched', 'Matched With Ticket'),
            ('pr_matched', 'Matched with Payment Request'),
            ('unmatched', 'Unmatched'),
            ('unused_ticket', 'Unused Ticket'),
            ('adm', 'Debit Memo'),
        ],
        required=True,
        default='unmatched',
        index=True,
        track_visibility='always',
    )
    investigation_tag = fields.Char(
        string="Unmatched Tag",
        index=True,
        readonly=False,
        track_visibility='onchange',
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

    @api.multi
    def _update_matching_status(self):
        for rec in self:
            if rec.order_line_id:
                rec.matching_status = 'order_matched'
            elif rec.payment_request_id:
                rec.matching_status = 'pr_matched'
            else:
                if rec.matching_status in ('unused_ticket', 'adm'):
                    continue
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
    def _match_with_sale_order(self):
        self.ensure_one()
        match_function = f'_match_{self.invoice_type}_with_sale_order'
        if hasattr(self, match_function):
            getattr(self, match_function)()
        else:
            raise MissingError(_("Method not implemented."))

    @api.multi
    def _match_with_sale_order_line(self):
        self.ensure_one()
        match_function = f'_match_{self.invoice_type}_with_sale_order_line'
        if hasattr(self, match_function):
            getattr(self, match_function)()
        else:
            raise MissingError(_("Method not implemented."))

    @api.multi
    def _match_with_payment_request(self):
        self.ensure_one()

        match_function = f'_match_{self.invoice_type}_with_payment_request'
        if hasattr(self, match_function):
            getattr(self, match_function)()
        else:
            raise MissingError(_("Method not implemented."))

    @api.multi
    def action_unused_tickets_invoice_lines(self):
        # TODO: we need more control, if one of the lines is already matched.
        # and the order or the PR has been sent to SAP. the user should not be
        # allowed to do such action.
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

    @api.model
    def _get_unmatched_invoice_lines(
            self, date_from=False, date_to=False, invoice_type=False):
        domain = [('matching_status', '=', 'unmatched')]
        if invoice_type:
            domain.append(('invoice_type', '=', invoice_type))
        if date_from:
            domain.append(('invoice_date', '>=', date_from))
        if date_to:
            domain.append(('invoice_date', '<=', date_to))
        return self.search(domain)

    @api.model
    @job(default_channel='root')
    def match_supplier_invoice_lines(self, date_from, date_to, invoice_type):
        unmatched_lines = self._get_unmatched_invoice_lines(
            date_from, date_to, invoice_type)
        for line in unmatched_lines:
            line.with_delay().match_with_sale_order()

    @api.multi
    def action_unlink_invoice(self):
        for rec in self:
            rec._unlink_invoice_line()

    @api.multi
    def _unlink_invoice_line(self):
        self.ensure_one()
        old_order_line = self.order_line_id
        old_payment_request = self.payment_request_id

        self.write({
            'order_line_id': False,
            'order_id': False,
            'payment_request_id': False,
        })

        if old_order_line:
            if not old_order_line.invoice_line_ids:
                old_order_line.matching_status = 'unmatched'
        if old_payment_request:
            if not old_payment_request.supplier_invoice_ids:
                old_payment_request.matching_status = 'unmatched'

    def _force_match_invoice_line(
            self, order_id=False, pr_id=False, line_id=False):
        self.ensure_one()
        if not order_id and not pr_id and not line_id:
            return
        if not order_id:
            order_id = self.order_id
        if pr_id and pr_id not in order_id.payment_request_ids:
            ValidationError(
                f"Payment request {pr_id.name} must belong to "
                f"{order_id.name}.")
        if line_id and line_id not in order_id.line_ids:
            ValidationError(
                f"Order line {line_id.name} must belong to "
                f"{order_id.name}.")

        # Remove the current link in the invoice line.
        if self.order_id:
            self._unlink_invoice_line()

        # Link the invoice line with the new record.
        self.order_id = order_id

        if pr_id:
            return pr_id.write({
                'supplier_invoice_ids': [(4, self.id)],
                'matching_status': 'matched',
            })
        if line_id:
            return line_id.write({
                'invoice_line_ids': [(4, self.id)],
                'matching_status': 'matched',
            })

    @api.multi
    def action_update_investigation_tag(self, investigation_tag):
        return self.write({
            'investigation_tag': investigation_tag})
