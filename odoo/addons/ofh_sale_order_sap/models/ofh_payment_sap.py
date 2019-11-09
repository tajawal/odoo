# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class OfhPaymentSap(models.Model):
    _name = 'ofh.payment.sap'
    _description = 'Ofh Payment SAP'
    _inherit = 'sap.binding'
    _order = 'send_date desc'

    @api.multi
    @api.depends('sale_order_id', 'payment_request_id')
    def name_get(self):
        result = []
        for rec in self:
            if rec.sale_order_id:
                name = rec.sale_order_id.name
            else:
                name = rec.payment_request_id.track_id
            result.append((rec.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                ('sale_order_id.name', operator, name),
                ('payment_request_id.track_id', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
            else:
                domain = ['|'] + domain

        records = self.search(domain + args, limit=limit)
        return records.name_get()

    payment_id = fields.Many2one(
        string="Payment",
        comodel_name='ofh.payment',
        index=True,
        readonly=True,
        ondelete='cascade',
        auto_join=True
    )
    payment_request_id = fields.Many2one(
        string="Payment Request",
        comodel_name='ofh.payment.request',
        readonly=True,
        ondelete='cascade',
        index=True,
        auto_join=True
    )
    sap_payment_detail = fields.Text(
        string="SAP Payment Details",
        readonly=True,
    )
    payment_detail = fields.Text(
        string="Payment Details",
        readonly=True,
    )
    send_date = fields.Datetime(
        string="Sending Date",
        required=True,
        readonly=True,
        index=True,
    )
    state = fields.Selection(
        string="Integration Status",
        selection=[
            ('draft', 'Draft'),
            ('visualize', 'Simulation'),
            ('cancel_visualize', 'Simulation Cancelled'),
            ('success', 'Success'),
            ('failed', 'Failed'),
        ],
        index=True,
        default='draft',
        required=True,
        track_visibility='always',
    )
    sap_status = fields.Selection(
        string='SAP status',
        selection=[
            ('not_applicable', 'Not Applicable'),
            ('not_in_sap', "Not In SAP"),
            ('in_sap', "Sale In SAP")],
        default='not_applicable',
        required=True,
        index=True,
        readonly=True,
        track_visibility='always',
    )
    failing_reason = fields.Selection(
        string="Integration Reason",
        selection=[
            ('not_applicable', 'N/A'),
            ('skipped', "Skipped"),
            ('error', "Error"),
            ('investigate', 'Investigate')],
        default='not_applicable',
        required=True,
        index=True,
        track_visibility='onchange',
    )
    failing_text = fields.Char(
        string="Response",
        readonly=True,
    )
    sap_sale_order_id = fields.Many2one(
        comodel_name='ofh.sale.order.sap',
        readonly=True,
        ondelete='cascade',
        index=True,
        auto_join=True
    )
    sale_order_id = fields.Many2one(
        string="Sale Order",
        comodel_name='ofh.sale.order',
        readonly=True,
        ondelete='cascade',
        index=True,
        compute='_compute_sale_order_id',
        store=True,
    )
    is_enett = fields.Boolean(
        string="Is Enett?",
        compute='_compute_is_enett',
        readonly=True,
    )
    # SAP Payment Fields
    system = fields.Char(
        string="System",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    transaction = fields.Char(
        string="Transaction",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    company_code = fields.Char(
        string="Company Code",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    document_date = fields.Char(
        string="DocumentDate",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    header_text = fields.Char(
        string="HeaderText",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    reference = fields.Char(
        string="Reference",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    currency = fields.Char(
        string="Currency",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    account1 = fields.Char(
        string="Account1",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    account2 = fields.Char(
        string="Account2",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    amount1 = fields.Char(
        string="Amount1",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    amount2 = fields.Char(
        string="Amount2",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    bank_charge = fields.Char(
        string="Bank Charge",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    splgl = fields.Char(
        string="SPLGL",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    sales_office = fields.Char(
        string="Sales Office",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    material = fields.Char(
        string="Material",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    reference_key1 = fields.Char(
        string="Reference Key 1",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    reference_key2 = fields.Char(
        string="Reference Key 2",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    reference_key3 = fields.Char(
        string="Reference Key 3",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    assignment = fields.Char(
        string="Assignment",
        readonly=True,
        store=True,
        compute="_compute_sap_payment_detail",
        index=True,
    )
    line_item_text = fields.Char(
        string="Line Item Text",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    # Payment fields
    order_id = fields.Char(
        string="order_id",
        readonly=True,
        compute="_compute_payment_detail"
    )
    order_number = fields.Char(
        string="Order #",
        readonly=True,
        compute="_compute_payment_detail"
    )
    order_type = fields.Char(
        string="order_type",
        readonly=True,
        compute="_compute_payment_detail",
        store=True,
    )
    order_status = fields.Char(
        string="order_status",
        readonly=True,
        compute="_compute_payment_detail"
    )
    supplier_name = fields.Char(
        string="supplier_name",
        readonly=True,
        compute="_compute_payment_detail"
    )
    validating_carrier = fields.Char(
        string="validating_carrier",
        readonly=True,
        compute="_compute_payment_detail"
    )
    order_owner = fields.Char(
        string="order_owner",
        readonly=True,
        compute="_compute_payment_detail"
    )
    entity = fields.Selection(
        selection=[
            ('almosafer', 'Almosafer'),
            ('tajawal', 'Tajawal')],
        readonly=True,
        compute="_compute_payment_detail"
    )
    ahs_group_name = fields.Char(
        string="ahs_group_name",
        readonly=True,
        compute="_compute_payment_detail"
    )
    country_code = fields.Char(
        string="country_code",
        readonly=True,
        compute="_compute_payment_detail"
    )
    payment_provider = fields.Char(
        string="payment_provider",
        readonly=True,
        compute="_compute_payment_detail"
    )
    payment_source = fields.Char(
        string="payment_source",
        readonly=True,
        compute="_compute_payment_detail"
    )
    payment_method = fields.Char(
        string="payment_method",
        readonly=True,
        compute="_compute_payment_detail"
    )
    payment_mode = fields.Char(
        string="payment_mode",
        readonly=True,
        compute="_compute_payment_detail"
    )
    reference_id = fields.Char(
        string="reference_id",
        readonly=True,
        compute="_compute_payment_detail"
    )
    amount = fields.Char(
        string="amount",
        readonly=True,
        compute="_compute_payment_detail"
    )
    mid = fields.Char(
        string="mid",
        readonly=True,
        compute="_compute_payment_detail"
    )
    bank_name = fields.Char(
        string="bank_name",
        readonly=True,
        compute="_compute_payment_detail"
    )
    card_type = fields.Char(
        string="card_type",
        readonly=True,
        compute="_compute_payment_detail"
    )
    card_bin = fields.Char(
        string="card_bin",
        readonly=True,
        compute="_compute_payment_detail"
    )
    card_owner = fields.Char(
        string="card_owner",
        readonly=True,
        compute="_compute_payment_detail"
    )
    card_last_four = fields.Char(
        string="card_last_four",
        readonly=True,
        compute="_compute_payment_detail"
    )
    auth_code = fields.Char(
        string="auth_code",
        readonly=True,
        compute="_compute_payment_detail"
    )
    is_installment = fields.Boolean(
        string="is_installment",
        readonly=True,
        default=False,
        compute="_compute_payment_detail"
    )
    is_3d_secure = fields.Boolean(
        string="is_3d_secure",
        readonly=True,
        default=False,
        compute="_compute_payment_detail"
    )
    sap_xml = fields.Text(
        string="SAP XML",
        readonly=True,
    )
    created_at = fields.Datetime(
        string="Created At",
        readonly=True,
        store=False,
        related="payment_id.created_at"
    )
    track_id = fields.Char(
        string="Track ID",
        readonly=True,
        store=False,
        related="payment_id.track_id"
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    @api.multi
    @api.depends('payment_request_id', 'payment_id')
    def _check_sale_order_pr(self):
        for rec in self:
            if rec.payment_request_id or rec.payment_id:
                continue

            raise ValidationError(
                _("You've to specify a Payment or a Payment request."))

    @api.multi
    @api.depends('payment_id', 'sap_sale_order_id')
    def _compute_sale_order_id(self):
        for rec in self:
            if rec.payment_id:
                rec.sale_order_id = rec.payment_id.order_id
            else:
                rec.sale_order_id = rec.sap_sale_order_id.sale_order_id

    @api.multi
    @api.depends('sap_payment_detail')
    def _compute_sap_payment_detail(self):
        for rec in self:
            if rec.sap_payment_detail:
                payment_detail = json.loads(rec.sap_payment_detail)
            else:
                payment_detail = {}

            rec.system = payment_detail.get('System')
            rec.transaction = payment_detail.get('Transaction')
            rec.company_code = payment_detail.get('CompanyCode')
            rec.document_date = payment_detail.get('DocumentDate')
            rec.header_text = payment_detail.get('HeaderText')
            rec.reference = payment_detail.get('Reference')
            rec.currency = payment_detail.get('Currency')
            rec.account1 = payment_detail.get('Account1')
            rec.account2 = payment_detail.get('Account2')
            rec.amount1 = payment_detail.get('Amount1')
            rec.amount2 = payment_detail.get('Amount2')
            rec.bank_charge = payment_detail.get('BankCharge')
            rec.splgl = payment_detail.get('SPLGL')
            rec.sales_office = payment_detail.get('SalesOffice')
            rec.material = payment_detail.get('Material')
            rec.reference_key1 = payment_detail.get('ReferenceKey1')
            rec.reference_key2 = payment_detail.get('ReferenceKey2')
            rec.reference_key3 = payment_detail.get('ReferenceKey3')
            rec.assignment = payment_detail.get('Assignment')
            rec.line_item_text = payment_detail.get('LineItemText')

    @api.multi
    @api.depends('payment_detail')
    def _compute_payment_detail(self):
        for rec in self:
            if rec.payment_detail:
                payment_detail = json.loads(rec.payment_detail)
            else:
                payment_detail = {}

            rec.order_id = payment_detail.get('order_id')
            rec.order_number = payment_detail.get('name')
            rec.order_type = payment_detail.get('order_type')
            rec.order_status = payment_detail.get('order_status')
            rec.supplier_name = payment_detail.get('supplier_name')
            rec.validating_carrier = payment_detail.get('validating_carrier')
            rec.order_owner = payment_detail.get('order_owner')
            rec.entity = payment_detail.get('entity')
            rec.ahs_group_name = payment_detail.get('ahs_group_name')
            rec.country_code = payment_detail.get('country_code')
            rec.payment_provider = payment_detail.get('payment_provider')
            rec.payment_source = payment_detail.get('payment_source')
            rec.payment_method = payment_detail.get('payment_method')
            rec.payment_mode = payment_detail.get('payment_mode')
            rec.reference_id = payment_detail.get('reference_id')
            rec.amount = payment_detail.get('amount')
            rec.mid = payment_detail.get('mid')
            rec.bank_name = payment_detail.get('bank_name')
            rec.card_type = payment_detail.get('card_type')
            rec.card_bin = payment_detail.get('card_bin')
            rec.card_owner = payment_detail.get('card_owner')
            rec.card_last_four = payment_detail.get('card_last_four')
            rec.auth_code = payment_detail.get('auth_code')
            rec.is_installment = payment_detail.get('is_installment')
            rec.is_3d_secure = payment_detail.get('is_3d_secure')

    @api.multi
    def _get_payment_payload(self):
        self.ensure_one()
        payload = json.loads(self.payment_detail)
        payload['external_id'] = self.id
        return payload

    @api.multi
    @api.depends('payment_id', 'payment_request_id')
    def _compute_is_enett(self):
        for rec in self:
            rec.is_enett = not rec.payment_id and not rec.payment_request_id
