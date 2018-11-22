# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
        return self.search([('state', 'in', ('ready', 'not_in_pr'))])

    @api.model
    def match_supplier_invoice_lines(self):
        """[summary]
        """
        pr_model = self.env['ofh.payment.request']
        # Get all the invoice lines that haven't been matched yet.
        pending_lines = self._get_pending_invoice_lines()

        # This is an ultimate case goal but can happen.
        if not pending_lines:
            return

        unreconciled_prs = pr_model._get_unreconciled_payment_requests()
        # If all PRS are reconciled. Means the payment request related to
        # selected invoices are not synchronised yet.
        if not unreconciled_prs:
            return pending_lines.write({'state': 'not_in_pr'})
        from_string = fields.Date.from_string
        # Pivot the supplier lines by date and locator
        lines_by_pnr = pending_lines._get_invoice_lines_by_pnr()
        for dt, invoice_status_dict in lines_by_pnr.items():
            for invoice_status, locator_dict in invoice_status_dict.items():
                # Add filter based on invoice_status
                if invoice_status == 'TKTT':
                    pr_type = 'charge'
                else:
                    pr_type = 'refund'

                for locator, lines in locator_dict.items():
                    payment_requests = unreconciled_prs.filtered(
                        lambda rec, inv_date=dt, inv_locator=locator,
                        pr_type=pr_type:
                        abs((from_string(inv_date) -
                            from_string(rec.created_at)).days) <= 2 and
                        (inv_locator in rec.record_locator or
                         inv_locator in rec.pnr) and
                        rec.request_type == pr_type)
                    if len(payment_requests) == 1:
                        payment_requests.write({
                            'supplier_invoice_ids': [(4, l.id) for l in lines],
                            'reconciliation_status': 'matched'})
                    elif len(payment_requests) > 1:
                        lines.message_post(
                            self._get_multiple_payment_request_message(
                                payment_requests))
                        lines.write({'state': 'not_matched'})
                    else:
                        lines.write({'state': 'not_matched'})

        # Once the matching logic is done we update all the payment request
        # that have not being matched with any invoice to investigate
        payment_requests = unreconciled_prs.filtered(
            lambda rec: not rec.supplier_invoice_ids)
        payment_requests.write({'reconciliation_status': 'investigate'})

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
    def _get_multiple_payment_request_message(self, payment_requests) -> str:
        """[summary]
        Arguments:
            payment_requests {[type]} -- [description]
        Returns:
            str -- message to be posted
        """
        msg = "Multiple payment request matched:\n{}".format(
            '\n- '.join(
                ['[{}] {}'.format(p.order_reference, p.track_id) for
                 p in payment_requests]))
        return msg
