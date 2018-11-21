# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhPaymentRequest(models.Model):

    _inherit = 'ofh.payment.request'

    supplier_invoice_ids = fields.One2many(
        string="Supplier costs",
        comodel_name='ofh.supplier.invoice.line',
        inverse_name='payment_request_id',
    )
    supplier_total_amount = fields.Monetary(
        string="Supplier Total Amount",
        currency_field='supplier_currency_id',
        compute='_compute_supplier_total_amount',
    )
    supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        comodel_name='res.currency',
        compute='_compute_supplier_total_amount',
    )

    # SAP related statuses
    reconciliation_status = fields.Selection(
        string="Supplier Status",
        selection=[
            ('pending', 'pending'),
            ('matched', 'Matched'),
            ('investigate', 'Investigate')],
        default='pending',
        required=True,
        index=True,
    )

    @api.model
    def _get_unreconciled_payment_requests(self):
        """
        Return Unreconcilided payment request
        """
        return self.search(
            [('reconciliation_status', 'in', ['pending', 'investigate'])])

    @api.multi
    @api.depends('supplier_invoice_ids', 'total_amount',
                 'request_type', 'order_type', 'order_amount',
                 'order_supplier_cost', 'order_supplier_currency')
    def _compute_supplier_total_amount(self):
        for rec in self:
            rec.supplier_total_amount = 0.0
            rec.supplier_currency_id = False
            # TODO: What about packages for now they're assuming like flights
            if rec.order_type != 'hotel':
                if rec.supplier_invoice_ids:
                    rec.supplier_total_amount = sum(
                        [inv.total for inv in rec.supplier_invoice_ids])
                    rec.supplier_currency_id = \
                        rec.supplier_invoice_ids.mapped('currency_id')[0]
                continue
            if rec.request_type == 'refund':
                rec.supplier_total_amount = \
                    ((rec.total_amount / rec.order_amount) *
                     rec.order_supplier_cost)
            else:
                # Case of amendment
                rec.supplier_total_amount = rec.total_amount
            rec.supplier_currency_id = rec.order_supplier_currency
