# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class OfhSaleOrder(models.Model):

    _inherit = 'ofh.sale.order'

    invoice_line_ids = fields.One2many(
        string="Invoice Lines",
        comodel_name='ofh.supplier.invoice.line',
        inverse_name='order_id',
    )
    air_india_commission = fields.Monetary(
        string="Air India Commission",
        compute='_compute_air_india_commission',
        readonly=True,
    )
    order_reconciliation_status = fields.Selection(
        string="Order Reconciliation Status",
        selection=[
            ('reconciled', 'Reconciled'),
            ('unreconciled', 'Unreconciled'),
            ('not_applicable', 'Not Applicable'),
        ],
        compute='_compute_order_reconciliation_status',
        default='unreconciled',
        readonly=True,
        store=True,
        index=True,
    )
    payment_request_reconciliation_status = fields.Selection(
        string="PR Reconciliation Status",
        selection=[
            ('reconciled', 'Reconciled'),
            ('unreconciled', 'Unreconciled'),
            ('not_applicable', 'Not Applicable'),
        ],
        compute='_compute_payment_request_reconciliation_status',
        default='unreconciled',
        readonly=True,
        store=True,
        index=True,
    )

    @api.multi
    @api.depends('line_ids.air_india_commission')
    def _compute_air_india_commission(self):
        for rec in self:
            rec.air_india_commission = sum(
                [l.air_india_commission for l in rec.line_ids])

    @api.multi
    def action_open_invoice_lines_with_pnr(self):
        self.ensure_one()
        if not self.supplier_reference:
            return {}
        domain = [
            '!',
            ('locator', 'like', self.supplier_reference),
            ('locator', 'like', self.vendor_reference)]
        return {
            'name': _(f"Invoice lines"),
            'type': "ir.actions.act_window",
            'res_model': "ofh.supplier.invoice.line",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain,
        }

    @api.multi
    @api.depends('line_ids.reconciliation_status')
    def _compute_order_reconciliation_status(self):
        for rec in self:
            if all([l.reconciliation_status == 'not_applicable'
                    for l in rec.line_ids]):
                rec.order_reconciliation_status = 'not_applicable'
                continue
            if all([l.reconciliation_status in ('reconciled', 'not_applicable')
                    for l in rec.line_ids]):
                rec.order_reconciliation_status = 'reconciled'
                continue
            rec.order_reconciliation_status = 'unreconciled'

    @api.multi
    @api.depends('payment_request_ids.reconciliation_status')
    def _compute_payment_request_reconciliation_status(self):
        for rec in self:
            if all([l.reconciliation_status == 'not_applicable'
                    for l in rec.payment_request_ids]):
                rec.payment_request_reconciliation_status = 'not_applicable'
                continue
            if all([l.reconciliation_status in ('reconciled', 'not_applicable')
                    for l in rec.payment_request_ids]):
                rec.payment_request_reconciliation_status = 'reconciled'
                continue
            rec.payment_request_reconciliation_status = 'unreconciled'

    @api.multi
    def action_initial_booking_not_applicable(self, not_applicable_flag):
        for rec in self:
            if rec.line_ids:
                rec.line_ids.action_matching_status_not_applicable(
                    not_applicable_flag=not_applicable_flag)
