# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class OfhSaleOrderSap(models.Model):
    _name = 'ofh.sale.order.sap'
    _inherit = 'sap.binding'
    _description = 'Ofh Sale Order SAP'
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

    order_detail = fields.Text(
        string="Order Details",
        readonly=True,
    )
    sap_header_detail = fields.Text(
        string="SAP Header Details",
        readonly=True,
    )
    send_date = fields.Datetime(
        string="Send to Sap At",
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
        readonly=True,
    )
    payment_state = fields.Selection(
        string="Payment Integration Status",
        sselection=[
            ('draft', 'Draft'),
            ('visualize', 'Simulation'),
            ('cancel_visualize', 'Simulation Cancelled'),
            ('success', 'Success'),
            ('failed', 'Failed'),
        ],
        readonly=True,
        store=False,
        related='sap_payment_ids.state',
    )
    sap_status = fields.Selection(
        string='Sale SAP status',
        selection=[
            ('not_applicable', 'Not Applicable'),
            ('not_in_sap', "Not In SAP"),
            ('in_sap', "Sale In SAP")],
        default='not_in_sap',
        required=True,
        index=True,
        readonly=True,
        track_visibility='always',
    )
    payment_sap_status = fields.Selection(
        string="Payment SAP Status",
        selection=[
            ('not_applicable', 'Not Applicable'),
            ('not_in_sap', "Not In SAP"),
            ('in_sap', "Sale In SAP")],
        readonly=True,
        store=False,
        related='sap_payment_ids.sap_status',
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
        readonly=True,
        track_visibility='onchange',
    )
    failing_text = fields.Char(
        string="Response Text",
        readonly=True,
    )
    sale_order_id = fields.Many2one(
        string="Sale Order",
        comodel_name='ofh.sale.order',
        readonly=True,
        ondelete='cascade',
        index=True,
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
    sap_line_ids = fields.One2many(
        string="SAP Lines",
        comodel_name="ofh.sale.order.line.sap",
        inverse_name='sap_sale_order_id',
        readonly=True,
    )
    sap_payment_ids = fields.One2many(
        string="SAP Payments",
        comodel_name="ofh.payment.sap",
        inverse_name='sap_sale_order_id',
        readonly=True,
    )
    is_double_hoop = fields.Boolean(
        string="Is Double Hoop?",
        default=False,
        index=True,
    )
    # SAP Header Fields
    system_id = fields.Char(
        string="System ID",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    sales_type = fields.Char(
        string="Sales Type",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    collection_mode = fields.Char(
        string="Collection Mode",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    booking_entity = fields.Char(
        string="Booking Entity",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    booking_number = fields.Char(
        string="Booking Number",
        readonly=True,
        store=True,
        compute="_compute_sap_header_detail"
    )
    sales_office = fields.Char(
        string="Sales Office",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    channel = fields.Char(
        string="Channel",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    customer = fields.Char(
        string="Customer",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    file_id = fields.Char(
        string="File ID",
        readonly=True,
        compute="_compute_sap_header_detail",
        index=True,
        help="File ID must be stored bc it will be used to check if the order "
             "is in SAP or not.",
    )
    booking_date = fields.Char(
        string="Booking Date",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    fe_indicator = fields.Char(
        string="FE Indicator",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    invoice_currency = fields.Char(
        string="Invoice Currency",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    tapro_invoice_number = fields.Char(
        string="Tapro Invoice Number",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    # Sale Order Header Fields
    name = fields.Char(
        string="Order ID",
        readonly=True,
        compute="_compute_order_detail"
    )
    order_id = fields.Char(
        string="Order ID",
        readonly=True,
        compute="_compute_order_detail"
    )
    entity = fields.Selection(
        selection=[
            ('almosafer', 'Almosafer'),
            ('tajawal', 'Tajawal')],
        readonly=True,
        compute="_compute_order_detail"
    )
    currency = fields.Char(
        string="Currency",
        readonly=True,
        compute="_compute_order_detail"
    )
    ahs_group_name = fields.Char(
        string="AHS Group Name",
        readonly=True,
        compute="_compute_order_detail"
    )
    country_code = fields.Char(
        string="Country Code",
        readonly=True,
        compute="_compute_order_detail"
    )
    is_egypt = fields.Boolean(
        string="Is Egypt",
        readonly=True,
        compute="_compute_order_detail"
    )
    sap_xml = fields.Text(
        string="SAP XML",
        readonly=True,
    )
    is_refund = fields.Boolean(
        string='Is Refund?',
        default=False,
        index=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    order_type = fields.Char(
        string="Order Type",
        readonly=True,
        compute="_compute_order_type",
        store=True,
    )

    @api.multi
    @api.depends('payment_request_id', 'sale_order_id')
    def _check_sale_order_pr(self):
        for rec in self:
            if rec.payment_request_id or rec.sale_order_id:
                continue

            raise ValidationError(
                _("You've to specify a Sale Order or a Payment request."))

    @api.multi
    @api.depends('order_detail')
    def _compute_order_detail(self):
        for rec in self:
            if rec.order_detail:
                order_detail = json.loads(rec.order_detail)
            else:
                order_detail = {}

            rec.name = order_detail.get('name')
            rec.order_id = order_detail.get('order_id')
            rec.entity = order_detail.get('entity')
            rec.currency = order_detail.get('currency')
            rec.ahs_group_name = order_detail.get('ahs_group_name')
            rec.country_code = order_detail.get('country_code')
            rec.is_egypt = order_detail.get('is_egypt')

    @api.multi
    @api.depends('sap_header_detail')
    def _compute_sap_header_detail(self):
        for rec in self:
            if rec.sap_header_detail:
                sap_header_detail = json.loads(rec.sap_header_detail)
            else:
                sap_header_detail = {}

            rec.system_id = sap_header_detail.get("SystemID")
            rec.sales_type = sap_header_detail.get("SalesType")
            rec.collection_mode = sap_header_detail.get("CollectionMode")
            rec.booking_entity = sap_header_detail.get("BookingEntity")
            rec.booking_number = sap_header_detail.get("BookingNumber")
            rec.sales_office = sap_header_detail.get("SalesOffice")
            rec.channel = sap_header_detail.get("Channel")
            rec.customer = sap_header_detail.get("Customer")
            rec.file_id = sap_header_detail.get("FileID")
            rec.booking_date = sap_header_detail.get("BookingDate")
            rec.fe_indicator = sap_header_detail.get("FEIndicator")
            rec.invoice_currency = sap_header_detail.get("InvoiceCurrency")
            rec.tapro_invoice_number = sap_header_detail.get(
                "TaproInvoiceNumber")

    @api.multi
    def _get_sale_payload(self):
        self.ensure_one()
        payload = json.loads(self.order_detail)
        payload['external_id'] = self.id
        line_items = []
        line_index = 0
        for line in self.sap_line_ids:
            line_payload = json.loads(line.line_detail)
            line_payload['external_id'] = line.id
            line_index += 1
            line_payload['line_index'] = line_index
            line_items.append(line_payload)
        payload['line_items'] = line_items
        return payload

    @api.multi
    @api.depends('payment_request_id', 'sale_order_id')
    def _compute_order_type(self):
        for rec in self:
            if rec.payment_request_id:
                rec.order_type = rec.payment_request_id.order_type
            elif rec.sale_order_id:
                rec.order_type = rec.sale_order_id.order_type

    @api.multi
    def action_mark_order_as_not_applicable(self):
        sales = self.filtered(
            lambda r: r.sale_order_id).mapped(
            'sale_order_id')
        if sales:
            sales.action_sale_not_applicable()
        prs = self.filtered(
            lambda r: r.payment_request_id).mapped(
            'payment_request_id')
        if prs:
            prs.action_sale_not_applicable()
