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
    supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        comodel_name='res.currency',
        related='supplier_invoice_ids.currency_id',
        readonly=True,
    )
    supplier_total_amount = fields.Monetary(
        string="Supplier Total Amount",
        currency_field='supplier_currency_id',
        compute='_compute_supplier_total_amount',
        readonly=True,
        help="Supplier total amount without Shamel cost",
    )
    supplier_shamel_total_amount = fields.Monetary(
        string="Supplier Shamel Total Amount",
        currency_field='supplier_currency_id',
        compute='_compute_supplier_total_amount',
        readonly=True,
        help="Supplier total amount including Shamel cost",
    )
    supplier_office_id = fields.Char(
        compute='_compute_office_id',
        search='_search_office_id',
        store=False,
        readonly=True,
    )

    @api.multi
    @api.depends('supplier_invoice_ids.gds_net_amount',
                 'supplier_invoice_ids.total', 'total_amount',
                 'request_type', 'order_type', 'order_amount', 'currency_id',
                 'order_supplier_cost', 'order_supplier_currency_id',
                 'matching_status', 'fare_difference', 'insurance',
                 'penalty')
    def _compute_supplier_total_amount(self):
        for rec in self:
            rec.supplier_total_amount = rec.supplier_shamel_total_amount = 0.0
            rec.supplier_currency_id = False
            # TODO: What about packages for now they're assuming like flights
            if rec.order_type != 'hotel':
                if rec.supplier_invoice_ids:
                    kwd_invoices = rec.supplier_invoice_ids.filtered(
                        lambda i: i.currency_id == self.env.ref('base.KWD'))
                    rec.supplier_total_amount = sum(
                        [i.gds_net_amount if i.invoice_type == 'gds' else
                         i.total for i in rec.supplier_invoice_ids])
                    rec.supplier_currency_id = \
                        rec.supplier_invoice_ids.mapped('currency_id')[0]
                    if not kwd_invoices:
                        continue
                    # Shamel cost minimum is 2 KWD. we take the absolute value
                    # because the cost will be negative in case of refund.
                    shamel_cost = max(abs(sum(
                        [inv.gds_alshamel_cost for inv in kwd_invoices])), 2)
                    rec.supplier_shamel_total_amount = \
                        rec.supplier_total_amount + shamel_cost
                # If a flight don't match with any supplier invoice and is
                # marked as not applicable we reverse calculate the cost using
                # the fees of the payment request.
                elif rec.matching_status == 'not_applicable':
                    if rec.request_type == 'charge':
                        rec.supplier_total_amount = \
                            rec.fare_difference + rec.insurance + rec.penalty
                    elif rec.request_type == 'refund':
                        rec.supplier_total_amount = \
                            rec.fare_difference - rec.insurance - rec.penalty
                    rec.supplier_currency_id = \
                        rec.order_supplier_currency_id or rec.currency_id
                continue
            if rec.request_type == 'refund':
                if rec.order_amount:
                    rec.supplier_total_amount = \
                        ((rec.total_amount / rec.order_amount) *
                         rec.order_supplier_cost)
                    rec.supplier_currency_id = rec.order_supplier_currency_id
            else:
                # Case of amendment
                rec.supplier_total_amount = rec.total_amount
                rec.supplier_currency_id = rec.currency_id

    @api.multi
    @api.depends('supplier_invoice_ids.office_id')
    def _compute_office_id(self):
        for rec in self:
            if not rec.supplier_invoice_ids:
                rec.supplier_office_id = ''
                continue
            rec.supplier_office_id = ','.join(
                set([i.office_id for i in rec.supplier_invoice_ids
                     if i.office_id]))

    @api.multi
    def _search_office_id(self, operator, value):
        return [('supplier_invoice_ids.office_id', operator, value)]
