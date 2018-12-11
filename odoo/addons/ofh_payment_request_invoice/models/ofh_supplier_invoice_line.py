# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.queue_job.job import job


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
        from_string = fields.Date.from_string
        if self.env.context.get('forced'):
            return self.write({'state': 'forced'})
        for rec in self:
            if not rec.payment_request_id:
                rec.state = 'not_matched'
                continue
            day_diff = \
                abs((from_string(rec.payment_request_id.created_at) -
                    from_string(rec.invoice_date))).days
            if day_diff == 0:
                rec.state = 'matched'
            elif day_diff <= 2:
                rec.state = 'suggested'

    @api.model
    def _get_pending_invoice_lines(self):
        return self.search([('state', 'in', ('ready', 'not_matched'))])

    @api.multi
    def unlink_payment_request(self):
        return self.write({
            'payment_request_id': False,
        })

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
        """Match supplier invoice lines with payment request.
        """
        pr_model = self.env['ofh.payment.request']
        # Get all the invoice lines that haven't been matched yet.
        pending_lines = self._get_pending_invoice_lines()

        # This is an ultimate case goal but can happen.
        if not pending_lines:
            return self.env.user.notify_info(
                "No Supplier Invoice Line available for matching.")

        unreconciled_prs = pr_model._get_unreconciled_payment_requests()
        # If all PRS are reconciled. Means the payment request related to
        # selected invoices are not synchronised yet.
        if not unreconciled_prs:
            pending_lines.write({'state': 'not_matched'})
            return self.env.user.notify_info(
                "No Payment Request available for matching.")
        from_str = fields.Date.from_string
        # Pivot the supplier lines by date and locator
        lines_by_pnr = pending_lines._get_invoice_lines_by_pnr()
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
        for pr in pr_by_invoices:
            lines = pr_by_invoices[pr].filtered(
                lambda i: not i.payment_request_id)
            lines_with_multiple_match = pr_by_invoices[pr] - lines
            for line in lines_with_multiple_match:
                # TODO: Add activity to investigate those invoices.
                line.message_post(
                    self._get_multiple_payment_request_message(pr))
            pr.write({
                'supplier_invoice_ids': [(4, l.id) for l in lines],
                'reconciliation_status': 'matched'})

        # Once the matching logic is done we update all the payment request
        # that have not being matched with any invoice to investigate
        payment_requests = unreconciled_prs.filtered(
            lambda rec: not rec.supplier_invoice_ids and
            rec.reconciliation_status != 'investigate')
        payment_requests.write({'reconciliation_status': 'investigate'})

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
