# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    payment_request_id = fields.Many2one(
        string="Payment request",
        comodel_name='ofh.payment.request',
        readonly=True,
        index=True,
        track_visibility='always',
        auto_join=True
    )

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
            unmatched_prs.write({'matching_status': 'unmatched'})

    @api.multi
    def _update_payment_request(self, payment_request):
        """Force match a supplier invoice with the given payment request
        Arguments:
            payment_request {ohf.payment.request} -- payment request record
        """
        if not payment_request:
            return False

        self.write({'payment_request_id': payment_request.id})
        payment_request.write({'matching_status': 'matched'})
        return True
