# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


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
    is_full_refund = fields.Boolean(
        string='Is Full Refund?',
        compute='_compute_is_full_refund',
        store=True,
        readonly=True,
    )

    @api.multi
    @api.depends('payment_request_ids.matching_status')
    def _compute_payment_request_matching_status(self):
        for rec in self:
            if all([l.matching_status == 'not_applicable'
                    for l in rec.payment_request_ids]):
                rec.payment_request_matching_status = 'not_applicable'
                continue
            if all([l.matching_status in ('matched', 'not_applicable')
                    for l in rec.payment_request_ids]):
                rec.payment_request_matching_status = 'matched'
                continue
            rec.payment_request_matching_status = 'unmatched'

    @api.multi
    @api.depends('payment_request_ids')
    def _compute_is_full_refund(self):
        for rec in self:
            rec.is_full_refund = False
            if len(rec.payment_request_ids) != 1:
                continue
            if rec.payment_request_ids[0].request_type != 'refund':
                continue
            rec.is_full_refund = float_compare(
                rec.payment_request_ids[0].order_amount,
                rec.payment_request_ids[0].total_amount,
                precision_rounding=rec.currency_id.rounding) == 0
