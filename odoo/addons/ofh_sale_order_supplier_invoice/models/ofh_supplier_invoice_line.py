# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.addons.queue_job.job import job
from odoo.exceptions import MissingError


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
            ('order_matched', 'Matched With Ticket'),
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
