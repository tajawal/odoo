# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class OfhSaleOrder(models.Model):

    _inherit = ['ofh.sale.order']

    payment_request_ids = fields.One2many(
        comodel_name="ofh.payment.request",
        string="Payment Request IDs",
        inverse_name='order_id',
        readonly=True,
    )
    payment_request_matching_status = fields.Selection(
        string="Payment Request Matching Status",
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable')],
        compute='_compute_payment_request_matching_status',
        store=True,
        index=True,
        readonly=True,
        default='unmatched',
        track_visibility='onchange',
    )

    @api.multi
    @api.depends('payment_request_ids.reconciliation_status')
    def _compute_payment_request_matching_status(self):
        for rec in self:
            pass
