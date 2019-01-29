# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    payment_request_id = fields.Many2one(
        string="Payment request",
        comodel_name='ofh.payment.request',
        inverse='_inverse_payment_request_id',
        readonly=True,
        track_visibility='always',
    )

    @api.multi
    def _inverse_payment_request_id(self):
        from_str = fields.Date.from_string
        if self.env.context.get('forced'):
            return self.write({'state': 'forced'})
        not_matched = matched = suggested = self.browse()
        for rec in self:
            if not rec.payment_request_id:
                not_matched |= rec
                continue
            day_diff = abs((from_str(
                rec.payment_request_id.created_at) - from_str(
                    rec.invoice_date)).days)
            if day_diff == 0:
                matched |= rec
            elif day_diff <= 2:
                suggested |= rec
        if not_matched:
            not_matched.write({'state': 'not_matched'})
        if matched:
            matched.write({'state': 'matched'})
        if suggested:
            suggested.write({'state': 'suggested'})

    @api.model
    def _get_pending_invoice_lines(self, min_date=False):
        domain = [('state', 'in', ('ready', 'not_matched'))]
        if min_date:
            domain.append(('invoice_date', '>=', min_date))
        return self.search(domain)

    @api.multi
    def unlink_payment_request(self):
        old_payment_requests = self.mapped('payment_request_id')
        self.write({
            'payment_request_id': False,
        })
        # Find PRs that aren't matching any more.
        unmatched_prs = old_payment_requests.filtered(
            lambda rec: not rec.supplier_invoice_ids)
        if unmatched_prs:
            unmatched_prs.write({'reconciliation_status': 'investigate'})

    @api.multi
    def _update_payment_request(self, payment_request):
        """Force match a supplier invoice with the given payment request
        Arguments:
            payment_request {ohf.payment.request} -- payment request record
        """
        if not payment_request:
            return False

        self.with_context(forced=True).write({
            'payment_request_id': payment_request.id})
        payment_request.write({'reconciliation_status': 'matched'})
        return True

    @api.model
    @job(default_channel='root')
    def match_supplier_invoice_lines(self):
        """Match supplier invoice lines with payment request."""
        _logger.info('Matching payment requests with invoice lines')

        # Get all payment requests that haven't been matched yet.
        pr_model = self.env['ofh.payment.request']
        _logger.info('Get payment request matching condidates')
        unreconciled_prs = pr_model._get_unreconciled_payment_requests()
        if not unreconciled_prs:
            return self.env.user.notify_info(
                "No Payment Request available for matching.")
        _logger.info(
            '%s payments request matching condidates', len(unreconciled_prs))

        # Get all the invoice lines that haven't been matched yet.
        _logger.info('Get invoice lines matching condidates')

        # beceause prs are ordered by creation date ASC we're allowed to do
        # the following
        min_date = fields.Date.to_string(
            fields.Date.from_string(unreconciled_prs[0].created_at) -
            relativedelta(days=3))
        pending_lines = self._get_pending_invoice_lines(min_date=min_date)

        # This is an ultimate case goal but can happen.
        if not pending_lines:
            return self.env.user.notify_info(
                "No Supplier Invoice Line available for matching.")
        _logger.info('%s lines matching condidates found', len(pending_lines))

        from_str = fields.Date.from_string

        # Pivot the supplier lines by date and locator
        lines_by_pnr = pending_lines._get_invoice_lines_by_pnr()

        _logger.info('Matching payment requests with invoice lines started.')
        pr_by_invoices = {}
        for pr in unreconciled_prs:
            for dt in lines_by_pnr:
                if abs((from_str(dt) - from_str(pr.created_at)).days) > 2:
                    continue
                for status in lines_by_pnr[dt]:
                    pr_type = \
                        'charge' if status in ('TKTT', 'AMND') else 'refund'
                    if pr.request_type != pr_type:
                        continue
                    for locator in lines_by_pnr[dt][status]:
                        if locator in pr.supplier_reference:
                            pr_by_invoices.setdefault(pr, self.browse())
                            pr_by_invoices[pr] |= \
                                lines_by_pnr[dt][status][locator]
        _logger.info(
            "Matching payment requests with invoice lines is done."
            "Updating the matched invoice lines with the payment request.")

        reconciled_prs = pr_model.browse()
        for pr in pr_by_invoices:
            supplier_invoice_ids = []
            for line in pr_by_invoices[pr]:
                if line.payment_request_id:
                    line.message_post(
                        self._get_multiple_payment_request_message(pr))
                else:
                    supplier_invoice_ids.append(((4, line.id)))
            pr.write({
                'supplier_invoice_ids': supplier_invoice_ids,
                'reconciliation_status': 'matched'})
            if pr.need_to_investigate:
                reconciled_prs |= pr

        # Once the matching logic is done we update all the payment request
        # that have not being matched with any invoice to investigate
        _logger.info(
            "Updating status of unmatched payment requests to investigate.")

        payment_requests = unreconciled_prs.filtered(
            lambda rec: not rec.supplier_invoice_ids and
            rec.reconciliation_status != 'investigate')

        payment_requests.write({'reconciliation_status': 'investigate'})

        reconciled_prs.optmise_matching_result()

        # reconciled_prs.matching_optimizations()
        return self.env.user.notify_info(
            "Matching with Supplier Invoices is done.")

    @api.multi
    def _get_invoice_lines_by_pnr(self) -> dict:
        """Group the invoice line by date and locator.
        Returns:
            dict -- {'{invoice_date}': {
                '{invoice_status}': {
                    '{locator}': ofh.supplier.invoice.line(id1, id2)}}}
        """
        invoice_line_by_pnr = {}
        for line in self:
            invoice_line_by_pnr.setdefault(line.invoice_date, {})
            invoice_line_by_pnr[line.invoice_date].setdefault(
                line.invoice_status, {})
            invoice_line_by_pnr[line.invoice_date][line.invoice_status].\
                setdefault(line.locator, line.browse())
            invoice_line_by_pnr[
                line.invoice_date][line.invoice_status][line.locator] |= line
        return invoice_line_by_pnr

    @api.model
    def _get_multiple_payment_request_message(self, payment_request) -> str:
        """[summary]
        Arguments:
            payment_requests {[type]} -- [description]
        Returns:
            str -- message to be posted
        """
        return "This supplier line also matched with:{}".format(
            payment_request.track_id)
