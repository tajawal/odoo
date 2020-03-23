# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from odoo import api, fields, models
from odoo.addons.queue_job.job import job
from odoo.tools import float_compare, float_is_zero

BRANCH_REGIONS = ['CR', 'WR', 'ER', 'SR', 'NR']
UNIFY_STORE_ID = "1000"
GROUP_ID = "7"


class OfhSaleOrder(models.Model):
    _name = 'ofh.sale.order'
    _description = 'Ofh Sale Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = None

    @api.model
    def _get_order_status_selection(self):
        return [
            ("10", "New"), ("15", "Tour Code in Progress"),
            ("18", "Booking in Progress"), ("25", "PNR in Progress"),
            ("30", "TST Error"), ("35", "TST in Progress"),
            ("39", "TST Created"), ("40", "New TF Booking"),
            ("41", "Incomplete TF booking"), ("42", "Unconfirmed TF Booking"),
            ("43", "Contact TF Support"), ("44", "Pending"),
            ("50", "Confirm Decision"), ("51", "Manually Ordered"),
            ("52", "Manual Confirm Queue"), ("53", "Manually Confirmed"),
            ("54", "Auto Confirm Started"), ("55", "Auto Confirm Queue"),
            ("56", "Auto Confirm in Progress"),
            ("57", "Auto Confirmed Partial Booking"),
            ("58", "Auto Confirmed"), ("60", "Auto Confirm Failed"),
            ("61", "Auto Confirm Cancelled"), ("62", "Auto Confirm Deleted"),
            ("64", "Manual Payment"), ("65", "Reprice Confirm Queue"),
            ("89", "Unprocessed"), ("91", "Failed"), ("94", "Cancelled"),
            ("95", "Refunded"), ("96", "Manually Cancelled"),
            ("100", "Duplicate"), ("101", "Cancellation under process"),
            ("102", "Cancellation cannot be processed"),
            ("200", "Reorder"), ("201", "Smart booking cancelled"),
            ("1000", "Mixed")
        ]

    @api.model
    def _get_payment_status_selection(self):
        return [
            ("79", 'Authorized - Risk flagged'), ("70", 'Error'),
            ("71", 'Pending'), ("72", 'Progress'), ("73", 'Timeout'),
            ("74", 'Empty'), ("77", 'Partial Paid'),
            ("76", 'Full Refund'), ("75", 'Partial Refund'),
            ("78", 'Authorized'), ("80", 'Captured'),
            ("83", 'Manually Captured'),
            ("81", 'Voided'), ("64", 'Manual Payment'), ("1000", 'Mixed')]

    @api.model
    def _get_payment_status_view_selection(self):
        return [
            ("11111", "Captured"), ("83027", "Refund"),
            ("83026", "Refund In Progress"), ("83025", "Refund Failed"),
            ("00000", "Declined"), ("10000", "Authorized"),
            ("20118", "Pending"), ("83035", "Void"), ("99999", "Deleted"),
            ("10100", "Flagged"), ("10100", "Flagged"), ('20068', 'Timeout'),
            ("20009", "Progress"), ("20010", "Partial Paid"),
        ]

    name = fields.Char(
        string="Order ID",
        readonly=True,
        required=True,
        index=True,
    )
    order_ids = fields.Char(
        string="Order IDs",
        compute='_compute_name',
        search='_search_name',
        store=False,
        readonly=True,
    )
    created_at = fields.Datetime(
        string="Created At",
        required=True,
        readonly=True,
        index=True,
    )
    updated_at = fields.Datetime(
        string="Updated At",
        required=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    track_id = fields.Char(
        string="Track ID",
        required=True,
        readonly=True,
        index=True,
    )
    order_type = fields.Selection(
        string="Order Type",
        selection=[
            ('hotel', 'Hotel'),
            ('flight', 'Flight'),
            ('package', 'Package'),
            ('other', 'Other')],
        required=True,
        readonly=True,
        index=True,
    )
    entity = fields.Selection(
        selection=[
            ('almosafer', 'Almosafer'),
            ('tajawal', 'Tajawal'),
            ('almosafer_branch', 'Almosafer Branch')],
        required=True,
        readonly=True,
        index=True,
    )
    order_status = fields.Selection(
        string="Order Status",
        selection=_get_order_status_selection,
        required=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    is_egypt = fields.Boolean(
        string="Is Egypt?",
        readonly=True,
        default=False,
        index=True,
    )
    order_owner = fields.Char(
        string="Order Owner",
        readonly=True,
    )
    is_pay_later = fields.Boolean(
        string="Is Pay Later?",
        readonly=True,
        default=False,
    )
    employee_discount_tag = fields.Char(
        string="Employee Discount Tag",
        readonly=True,
        default=False,
    )
    customer_discount_tag = fields.Char(
        string="Customer Discount Tag",
        readonly=True,
        default=False,
    )
    ahs_group_name = fields.Char(
        string="AHS Group Name",
        readonly=True,
    )
    customer_email = fields.Char(
        string="Customer Email",
        readonly=True,
    )
    customer_number = fields.Char(
        string="Customer Number",
        readonly=True,
    )
    agent_email = fields.Char(
        string="Agent Email",
        readonly=True,
    )
    country_code = fields.Char(
        string="Country Code",
        readonly=True,
    )
    booking_method = fields.Char(
        string="Booking Method",
        readonly=True,
    )
    point_of_sale = fields.Char(
        string="Point Of Sale",
        readonly=True,
        default=False,
    )
    payment_status = fields.Selection(
        string="payment Status",
        selection=_get_payment_status_selection,
        required=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    paid_at = fields.Datetime(
        string="Paid At",
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    store_id = fields.Char(
        string="Store ID",
        required=True,
        readonly=True,
        index=True,
    )
    group_id = fields.Char(
        string="Group ID",
        required=True,
        readonly=True,
        index=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name='res.currency',
        required=True,
        readonly=True,
        index=True,
    )
    vendor_currency_id = fields.Many2one(
        string="Vendor Currency",
        comodel_name='res.currency',
        readonly=True,
        index=True,
    )
    supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        comodel_name='res.currency',
        readonly=True,
    )
    total_vendor_cost = fields.Monetary(
        string="Total Vendor Cost",
        currency_field='vendor_currency_id',
        readonly=True
    )
    total_supplier_cost = fields.Monetary(
        string="Total Supplier Cost",
        currency_field='supplier_currency_id',
        readonly=True
    )
    total_amount = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    total_discount = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    total_tax = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    total_service_fee = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    total_insurance_amount = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    line_ids = fields.One2many(
        string="Lines",
        comodel_name='ofh.sale.order.line',
        inverse_name='order_id',
    )
    vendor_reference = fields.Char(
        string='Vendor Reference',
        compute='_compute_vendor_reference',
        readonly=True,
        # Storing this value to be able to search a search on it
        store=True,
        index=True,
        track_visibility='onchange',
    )
    locators = fields.Char(
        string="Locators",
        compute='_compute_locator',
        search='_search_locator',
        store=False,
        readonly=True,
    )
    supplier_reference = fields.Char(
        string="Supplier Reference",
        compute='_compute_supplier_reference',
        readonly=True,
        # Storing the value to be able to run a search on it
        store=True,
        index=True,
        track_visibility='onchange',
    )
    office_id = fields.Char(
        string="Office ID",
        compute='_compute_office_id',
        readonly=True,
        store=False,
        index=True,
    )
    ticketing_office_id = fields.Char(
        string="Ticketing Office ID",
        compute='_compute_ticketing_office_id',
        readonly=True,
        store=True,
        index=True,
        track_visibility='onchange',
    )
    hub_bind_ids = fields.One2many(
        comodel_name='hub.sale.order',
        inverse_name='odoo_id',
        string="Hub Bindings",
        readonly=True,
    )
    # Computed totals from lines
    lines_total_vendor_cost = fields.Monetary(
        string="Total computed vendor cost",
        compute='_compute_total_amounts',
        currency_field='vendor_currency_id',
        readonly=True,
        store=False,
    )
    lines_total_supplier_cost = fields.Monetary(
        string="Total computed supplier cost",
        compute='_compute_total_amounts',
        currency_field='supplier_currency_id',
        readonly=True,
        store=False,
    )
    lines_total_service_fee = fields.Monetary(
        string="Total computed service fee",
        compute='_compute_total_amounts',
        currency_field='currency_id',
        readonly=True,
        store=False,
    )
    lines_total_sale_price = fields.Monetary(
        string="Total computed sale price",
        compute='_compute_total_amounts',
        currency_field='currency_id',
        readonly=True,
        store=False,
    )
    lines_total_discount = fields.Monetary(
        string="Total computed discount",
        compute='_compute_total_amounts',
        currency_field='currency_id',
        readonly=True,
        store=False,
    )
    lines_total_tax = fields.Monetary(
        string="Total computed tax",
        compute='_compute_total_amounts',
        currency_field='currency_id',
        readonly=True,
        store=False,
    )
    lines_total_amount = fields.Monetary(
        string="Computed total Amount",
        compute='_compute_total_amounts',
        currency_field='currency_id',
        readonly=True,
        store=False,
    )
    order_matching_status = fields.Selection(
        string="Matching Status",
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable')],
        default='unmatched',
        compute='_compute_order_matching_status',
        store=True,
        index=True,
        readonly=True,
        track_visibility='onchange',
    )
    payment_ids = fields.One2many(
        string="Payments",
        comodel_name='ofh.payment',
        inverse_name='order_id',
        readonly=True
    )
    is_payment_different = fields.Boolean(
        string='Is payment different?',
        store=False,
        readonly=True,
        search='_search_is_payment_different',
        help="Technical field"
    )
    order_status_export = fields.Char(
        string="Order Status Export",
        compute='_compute_order_status_export',
        readonly=True,
        store=False,
    )
    payment_status_export = fields.Char(
        string="Payment Status Export",
        compute='_compute_payment_status_export',
        readonly=True,
        store=False,
    )
    supplier_name = fields.Char(
        string="Supplier Name",
        compute="_compute_supplier_name",
        store=True,
        track_visibility='onchange',
    )
    computed_payment_status = fields.Selection(
        string="Payment Status",
        selection=_get_payment_status_view_selection,
        readonly=True,
        index=True,
        track_visibility='onchange',
        compute="_compute_payment_status"
    )
    file_id = fields.Char(
        string="File Mongo ID",
        readonly=True,
        index=True,
    )
    file_reference = fields.Char(
        string="File ID",
        readonly=True,
        index=True,
    )
    file_references = fields.Char(
        string="File IDs",
        compute='_compute_file_reference',
        search='_search_file_reference',
        store=False,
        readonly=True,
    )
    ticket_sub_type = fields.Char(
        string="Ticket Sub Type",
        readonly=True,
    )
    is_unify = fields.Boolean(
        string="Is Unify",
        compute='_compute_unify',
        readonly=True,
        default=False,
    )
    booking_category = fields.Selection(
        selection=[
            ('amendment', 'Amendment'),
            ('initial', 'Initial')],
        index=True,
        readonly=True,
        default='initial',
    )
    sales_office = fields.Char(
        string="Sales Office",
        compute='_compute_sales_office',
        readonly=True,
        store=True,
    )
    branch_region = fields.Selection(
        string="Branch Region",
        selection=[('cr', 'CR'),
                   ('wr', 'WR'),
                   ('er', 'ER'),
                   ('sr', 'SR'),
                   ('nr', 'NR')],
        readonly=True,
        default='cr',
        compute='_compute_sales_office',
        store=True
    )
    amendment_fees = fields.Char(
        readonly=True,
    )
    fare_difference = fields.Monetary(
        string="Fare Difference",
        currency_field='currency_id',
        compute='_compute_amendment_fees',
        readonly=True,
        store=False,
    )
    change_fee = fields.Monetary(
        string="Change Fee",
        currency_field='currency_id',
        compute='_compute_amendment_fees',
        readonly=True,
        store=False,
    )
    booking_fee = fields.Monetary(
        string="Booking Fee",
        currency_field='currency_id',
        compute='_compute_amendment_fees',
        readonly=True,
        store=False,
    )
    insurance = fields.Monetary(
        currency_field='currency_id',
        compute='_compute_amendment_fees',
        readonly=True,
        store=False,
    )
    discount = fields.Monetary(
        currency_field='currency_id',
        compute='_compute_amendment_fees',
        readonly=True,
        store=False,
    )
    penalty = fields.Monetary(
        currency_field='currency_id',
        compute='_compute_amendment_fees',
        readonly=True,
        store=False,
    )
    adm_amount = fields.Monetary(
        string="ADM",
        currency_field='currency_id',
        compute='_compute_amendment_fees',
        readonly=True,
        store=False,
    )
    loss_amount = fields.Monetary(
        string="Losses",
        currency_field='currency_id',
        compute='_compute_amendment_fees',
        readonly=True,
        store=False,
    )
    loss_type = fields.Char(
        compute='_compute_amendment_fees',
        readonly=True,
        store=False,
    )
    input_vat_amount = fields.Monetary(
        string="Input VAT",
        currency_field='currency_id',
        compute='_compute_amendment_fees',
        readonly=True,
        store=False,
    )
    output_vat_amount = fields.Monetary(
        string="Output VAT",
        currency_field='currency_id',
        compute='_compute_amendment_fees',
        readonly=True,
        store=False,
    )
    manual_output_vat_amount = fields.Monetary(
        string="Manual Output VAT",
        currency_field='currency_id',
        help="Technical field to ajust VAT when neeeded",
        track_visibility='onchange',
    )
    total_amount = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        readonly=True,
    )
    tax_code = fields.Selection(
        string='Tax code',
        selection=[('ss', 'SS'), ('sz', 'SZ')],
        compute='_compute_amendment_fees',
        readonly=True,
        store=False,
    )
    # newly added VAT fields
    change_fee_vat_amount = fields.Monetary(
        string="Change Fee VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    fare_difference_vat_amount = fields.Monetary(
        string="Fare Difference VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    penalty_vat_amount = fields.Monetary(
        string="Penalty VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    adm_vat_amount = fields.Monetary(
        string="ADM VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    booking_fee_vat_amount = fields.Monetary(
        string="Booking Fee VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    deals_vat_amount = fields.Monetary(
        string="Deals VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    discount_vat_amount = fields.Monetary(
        string="Discount VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    initial_order_number = fields.Char(
        string="Initial Order",
        index=True,
        readonly=True,
    )
    initial_order = fields.Many2one(
        string="Initial Order",
        comodel_name='ofh.sale.order',
        inverse_name='initial_order_number',
        readonly=True,
        compute='_compute_initial_order',
        store=False,
    )
    payment_request_reason = fields.Char(
        string="Payment Request Reason",
        readonly=True,
    )
    payment_request_remarks = fields.Text(
        string="Payment Request Notes",
        readonly=True,
    )
    line_category = fields.Char(
        string="Sub Type",
        readonly=True,
        compute='_compute_line_category',
    )

    @api.model
    def _search_name(self, operator, value):
        if operator == 'ilike':
            ids = value.replace(" ", "").split(",")
            return [('name', 'in', ids)]
        return [('name', operator, value)]

    @api.multi
    @api.depends('name')
    def _compute_name(self):
        for rec in self:
            rec.order_ids = rec.name

    @api.model
    def _search_file_reference(self, operator, value):
        if operator == 'ilike':
            ids = value.replace(" ", "").split(",")
            return [('file_reference', 'in', ids)]
        return [('file_reference', operator, value)]

    @api.multi
    @api.depends('file_reference')
    def _compute_file_reference(self):
        for rec in self:
            rec.file_references = rec.file_reference

    @api.multi
    @api.depends('store_id')
    def _compute_unify(self):
        # For offline store_id is 1000
        for rec in self:
            rec.is_unify = bool(rec.store_id == UNIFY_STORE_ID)

    @api.multi
    @api.depends('initial_order_number')
    def _compute_initial_order(self):
        for rec in self:
            rec.initial_order = False
            if self.booking_category == "amendment" and self.initial_order_number:
                initial_order = self.search(
                    [("name", "=", self.initial_order_number)], limit=1)
                rec.initial_order = initial_order

    @api.multi
    def action_display_payments(self):
        self.ensure_one()
        if self.is_unify:
            payments = self.env['ofh.payment'].search(
                [('file_id', '=', self.file_id)])

            payment_ids = [p.id for p in payments]

            domain = [('id', 'in', payment_ids)]

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ofh.payment',
                'name': 'Payments',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': domain,
            }

    @api.multi
    @api.depends(
        'line_ids.vendor_confirmation_number',
        'line_ids.manual_vendor_confirmation_number')
    def _compute_vendor_reference(self):
        for rec in self:
            vendor_reference = []
            rec.vendor_reference = ''
            for line in rec.line_ids:
                if line.manual_vendor_confirmation_number:
                    vendor_reference.append(
                        line.manual_vendor_confirmation_number)
                else:
                    vendor_reference.append(line.vendor_confirmation_number)
            if vendor_reference:
                rec.vendor_reference = ', '.join(set(vendor_reference))

    @api.multi
    @api.depends('vendor_reference')
    def _compute_locator(self):
        for rec in self:
            rec.locators = rec.vendor_reference

    @api.model
    def _search_locator(self, operator, value):
        if operator == 'ilike':
            ids = value.replace(" ", "").split(",")
            return ['|', ('vendor_reference', 'in', ids), ('supplier_reference', 'in', ids)]
        return ['|', ('vendor_reference', operator, value), ('supplier_reference', operator, value)]

    @api.multi
    @api.depends(
        'line_ids.supplier_confirmation_number',
        'line_ids.manual_supplier_confirmation_number')
    def _compute_supplier_reference(self):
        for rec in self:
            supplier_reference = []
            rec.supplier_reference = ''
            for line in rec.line_ids:
                if line.manual_supplier_confirmation_number:
                    supplier_reference.append(
                        line.manual_supplier_confirmation_number)
                else:
                    supplier_reference.append(
                        line.supplier_confirmation_number)
            if supplier_reference:
                rec.supplier_reference = ', '.join(set(supplier_reference))

    @api.multi
    @api.depends('line_ids.office_id')
    def _compute_office_id(self):
        for rec in self:
            rec.office_id = ', '.join(
                set([r.office_id for r in rec.line_ids if r.office_id]))

    @api.multi
    @api.depends('line_ids.ticketing_office_id')
    def _compute_ticketing_office_id(self):
        for rec in self:
            rec.ticketing_office_id = ', '.join(
                set([r.ticketing_office_id for r in rec.line_ids
                     if r.ticketing_office_id]))

    @api.multi
    @api.depends('line_ids')
    def _compute_total_amounts(self):
        for rec in self:
            rec.lines_total_vendor_cost = rec.lines_total_service_fee = \
                rec.lines_total_sale_price = rec.lines_total_discount = \
                rec.lines_total_tax = rec.lines_total_amount = \
                rec.total_supplier_cost = 0.0
            for line in rec.line_ids:
                rec.lines_total_vendor_cost += line.vendor_cost_amount
                rec.lines_total_supplier_cost += line.supplier_cost_amount
                rec.lines_total_service_fee += line.service_fee_amount
                rec.lines_total_sale_price += line.sale_price
                rec.lines_total_discount += line.discount_amount
                rec.lines_total_tax += line.tax_amount
                rec.lines_total_amount += line.total_amount

    @api.multi
    @api.depends('line_ids.matching_status')
    def _compute_order_matching_status(self):
        for rec in self:
            if all([l.matching_status == 'not_applicable'
                    for l in rec.line_ids]):
                rec.order_matching_status = 'not_applicable'
                continue
            if all([l.matching_status in ('matched', 'not_applicable')
                    for l in rec.line_ids]):
                rec.order_matching_status = 'matched'
                continue
            rec.order_matching_status = 'unmatched'

    @api.model
    def _search_is_payment_different(self, operator, value):
        if operator == '!=':
            return [('id', '=', 0)]
        self.env.cr.execute("""
            SELECT s.id
            FROM ofh_sale_order as s,
            (SELECT order_id, SUM(total_amount) as paid_amount
             FROM ofh_payment
             GROUP BY order_Id) as f
            WHERE s.id = f.order_id AND
            abs(round(s.total_amount, 2) - round(f.paid_amount, 2)) > 0.1
        """)
        order_ids = [x[0] for x in self.env.cr.fetchall()]

        if not order_ids:
            return [('id', '=', 0)]
        return [('id', 'in', order_ids)]

    @api.multi
    def open_order_in_hub(self):
        """Open the order link to the payment request in hub using URL
        Returns:
            [dict] -- URL action dictionary
        """

        self.ensure_one()
        hub_backend = self.env['hub.backend'].search([], limit=1)
        if not hub_backend:
            return

        if self.is_unify:
            hub_url = "{}admin/unify/file/{}".format(
                hub_backend.hub_api_location, self.file_id)
        else:
            if self.booking_category == 'amendment':
                order_id = self.initial_order_number
            else:
                order_id = self.name

            hub_url = "{}admin/order/air/detail/{}".format(
                    hub_backend.hub_api_location, order_id)
        return {
            "type": "ir.actions.act_url",
            "url": hub_url,
            "target": "new",
        }

    @api.multi
    def action_update_orders_from_hub(self):
        for rec in self:
            rec.with_delay().action_update_hub_data()

    @job(default_channel='root.hub')
    @api.multi
    def action_update_hub_data(self):
        self.ensure_one()

        if self.booking_category == 'amendment' and not self.is_unify:
            order_id = self.track_id
        else:
            order_id = self.hub_bind_ids.external_id
        return self.hub_bind_ids.import_record(
            backend=self.hub_bind_ids.backend_id,
            external_id=order_id,
            force=True)

    @api.multi
    @api.depends('order_status')
    def _compute_order_status_export(self):
        for rec in self:
            order_statuses = self._fields['order_status'].selection(self)
            rec.order_status_export = dict(order_statuses) \
                .get(rec.order_status)

    @api.multi
    @api.depends('payment_status')
    def _compute_payment_status_export(self):
        for rec in self:
            payment_statuses = self._fields['payment_status'].selection(self)
            rec.payment_status_export = dict(payment_statuses) \
                .get(rec.payment_status)

    @api.multi
    @api.depends('line_ids.supplier_name')
    def _compute_supplier_name(self):
        for rec in self:
            if not rec.line_ids:
                continue
            rec.supplier_name = ','.join(set(
                [l.supplier_name for l in rec.line_ids]))

    @api.multi
    @api.depends('payment_ids.payment_status')
    def _compute_payment_status(self):
        for rec in self:
            if not rec.payment_ids:
                continue
            rec.computed_payment_status = rec.payment_ids[-1].payment_status

    @api.multi
    @api.depends('ahs_group_name')
    def _compute_sales_office(self):
        for rec in self:
            rec.sales_office = ''
            if rec.ahs_group_name and rec.ahs_group_name[:2] in BRANCH_REGIONS:
                rec.sales_office = rec.ahs_group_name[:4]
                rec.branch_region = rec.ahs_group_name[:2].lower()

    @api.multi
    @api.depends('amendment_fees', 'manual_output_vat_amount')
    def _compute_amendment_fees(self):
        for rec in self:
            fees = rec.amendment_fees
            if not fees:
                fees = '{}'

            fees_dict = json.loads(fees)
            if not fees_dict:
                rec.fare_difference = rec.change_fee = rec.penalty = \
                    rec.booking_fee = rec.discount = rec.input_vat_amount = \
                    rec.output_vat_amount = rec.adm_amount = 0.0
                rec.loss_type = ''
                rec.tax_code = 'sz'
            rec.fare_difference = fees_dict.get('fareDifference')
            rec.change_fee = fees_dict.get('changeFee')
            rec.penalty = fees_dict.get('penalty')
            rec.booking_fee = fees_dict.get('bookingFee')
            rec.discount = fees_dict.get('discount')
            rec.input_vat_amount = fees_dict.get('inputVat')

            # Sometimes the user correct manual the output vat amount.
            # For this reason we use the manual field instead the one fetched
            # from hub.
            if not float_is_zero(
                    rec.manual_output_vat_amount,
                    precision_rounding=rec.currency_id.rounding):
                rec.output_vat_amount = rec.manual_output_vat_amount
            else:
                rec.output_vat_amount = fees_dict.get('outputVat')

            rec.adm_amount = fees_dict.get('adm')
            rec.loss_type = fees_dict.get('lossType')
            # newly added vat fields
            rec.change_fee_vat_amount = fees_dict.get('changeFeeVat')
            rec.fare_difference_vat_amount = fees_dict.get('fareDifferenceVat')
            rec.penalty_vat_amount = fees_dict.get('penaltyVat')
            rec.adm_vat_amount = fees_dict.get('admVat')
            rec.booking_fee_vat_amount = fees_dict.get('bookingFeeVat')
            rec.deals_vat_amount = fees_dict.get('dealsVat')
            rec.discount_vat_amount = fees_dict.get('discountVat')
            if float_compare(
                    rec.output_vat_amount, 0.0,
                    precision_rounding=rec.currency_id.rounding) > 0:
                rec.tax_code = 'ss'
            else:
                rec.tax_code = 'sz'

    @api.multi
    @api.depends('line_ids.line_category')
    def _compute_line_category(self):
        if self.order_type == 'other':
            for rec in self:
                rec.line_category = self.line_ids.line_category
