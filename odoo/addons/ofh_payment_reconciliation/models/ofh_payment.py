# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.addons.queue_job.job import job


class OfhPayment(models.Model):
    _inherit = 'ofh.payment'

    payment_gateway_id = fields.Many2one(
        string="Payment Gateway",
        comodel_name='ofh.payment.gateway',
    )
    bank_settlement_id = fields.Many2one(
        string="Bank Settlement",
        related="payment_gateway_id.bank_settlement_id",
    )
    settlement_date = fields.Date(
        string="Bank Settlement Date",
        related="bank_settlement_id.settlement_date",
    )
    response_description = fields.Char(
        related="payment_gateway_id.response_description",
    )
    arn = fields.Char(
        related="payment_gateway_id.arn",
    )
    is_apple_pay = fields.Boolean(
        related="payment_gateway_id.is_apple_pay",
    )
    pg_payment_status = fields.Selection(
        string="PG Payment Status",
        related="payment_gateway_id.payment_status",
    )
    bank_name = fields.Selection(
        related="bank_settlement_id.bank_name",
    )
    gross_amount = fields.Monetary(
        related="bank_settlement_id.gross_amount",
    )
    net_transaction_amount = fields.Monetary(
        related="bank_settlement_id.net_transaction_amount",
    )
    pg_matching_status = fields.Selection(
        string="PG Matching Status",
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable')],
        default='unmatched',
        required=True,
        index=True,
        readonly=True,
    )
    reconciliation_status = fields.Selection(
        string="Reconciliation Status",
        selection=[
            ('reconciled', 'Reconciled'),
            ('unreconciled', 'Unreconciled'),
            ('not_applicable', 'Not Applicable'),
        ],
        default='unreconciled',
        compute='_compute_reconciliation_status',
        search='_search_reconciliation_status',
        index=True,
        readonly=True,
    )
    is_voided = fields.Boolean(
        string='Is Voided?',
        compute='_compute_is_voided',
        store=True,
        readonly=True,
    )
    assignment = fields.Char(
        string="Assignment",
        readonly=True,
        store=True,
        compute="_compute_assignment"
    )

    @api.multi
    @api.depends('sap_payment_ids.state', 'sap_payment_ids.assignment')
    def _compute_assignment(self):
        for rec in self:
            rec.assignment = ''
            sap_records = rec.sap_payment_ids.filtered(
                lambda p: p.state == 'success')
            if sap_records:
                rec.assignment = sap_records[-1].assignment

    @api.multi
    def action_pg_matching_applicable(self):
        return self.write({
            'pg_matching_status': 'unmatched',
        })

    @api.multi
    def action_pg_matching_not_applicable(self):
        return self.write({
            'pg_matching_status': 'not_applicable',
        })

    @api.multi
    @api.depends('payment_gateway_id')
    def _compute_reconciliation_status(self):
        for rec in self:
            rec.reconciliation_status = 'unreconciled'

            if rec.payment_gateway_id:
                rec.reconciliation_status = \
                    rec.payment_gateway_id.reconciliation_status
            continue

    @api.multi
    def _search_reconciliation_status(self, operator, value):
        return [('payment_gateway_id.reconciliation_status', operator, value)]

    @api.multi
    @api.depends('order_id')
    def _compute_is_voided(self):
        for rec in self:
            rec.is_voided = False
            if len(rec.order_id.payment_request_ids) != 1:
                continue
            if rec.order_id.payment_request_ids[0].request_type != 'void':
                continue
            rec.is_voided = True
