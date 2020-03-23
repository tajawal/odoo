# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class OfhSaleOrderLine(models.Model):

    _name = 'ofh.sale.order.line'
    _description = 'Ofh Sale Order Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = None

    @api.model
    def _get_order_status_selection(self):
        return self.env['ofh.sale.order']._get_order_status_selection()

    name = fields.Char(
        string="Product",
        required=True,
        readonly=True,
    )
    sequence = fields.Char(
        string="Sequence",
        readonly=True,
    )
    order_id = fields.Many2one(
        string="Order",
        required=True,
        readonly=True,
        index=True,
        comodel_name='ofh.sale.order',
        ondelete='cascade',
        auto_join=True,
    )
    order_ids = fields.Char(
        related='order_id.order_ids'
    )
    fare_difference = fields.Monetary(
        currency_field='currency_id',
        related='order_id.fare_difference',
        store=False,
    )
    change_fee = fields.Monetary(
        currency_field='currency_id',
        related='order_id.change_fee',
        store=False,
    )
    booking_fee = fields.Monetary(
        currency_field='currency_id',
        related='order_id.booking_fee',
        store=False,
    )
    insurance = fields.Monetary(
        related='order_id.insurance',
        store=False,
    )
    discount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.discount',
        store=False,
    )
    penalty = fields.Monetary(
        currency_field='currency_id',
        related='order_id.penalty',
        store=False,
    )
    adm_amount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.adm_amount',
        store=False,
    )
    loss_amount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.loss_amount',
        store=False,
    )
    loss_type = fields.Char(
        related='order_id.loss_type',
        store=False,
    )
    input_vat_amount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.input_vat_amount',
        store=False,
    )
    output_vat_amount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.output_vat_amount',
        store=False,
    )
    tax_code = fields.Selection(
        related='order_id.tax_code',
        store=False,
    )
    manual_output_vat_amount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.manual_output_vat_amount',
        track_visibility='onchange',
    )
    change_fee_vat_amount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.change_fee_vat_amount',
        store=False,
    )
    fare_difference_vat_amount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.fare_difference_vat_amount',
        store=False,
    )
    penalty_vat_amount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.penalty_vat_amount',
        store=False,
    )
    adm_vat_amount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.adm_vat_amount',
        store=False,
    )
    booking_fee_vat_amount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.booking_fee_vat_amount',
        store=False,
    )
    deals_vat_amount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.deals_vat_amount',
        store=False,
    )
    discount_vat_amount = fields.Monetary(
        currency_field='currency_id',
        related='order_id.discount_vat_amount',
        store=False,
    )
    created_at = fields.Datetime(
        string="Created At",
        required=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    updated_at = fields.Datetime(
        string="Updated At",
        required=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    line_type = fields.Selection(
        selection=[('hotel', 'Hotel'), ('flight', 'Flight')],
        string="Product Type",
        required=True,
        readonly=True,
        index=True,
    )
    line_category = fields.Char(
        string="Category",
        required=True,
        readonly=True,
    )
    state = fields.Selection(
        string="Status",
        selection=_get_order_status_selection,
        required=True,
        readonly=True,
        track_visibility='onchange',
    )
    is_domestic_ksa = fields.Boolean(
        string="Is Domestic KSA",
        readonly=True,
        default=False,
        help="True if the order is a domestic KSA, else False",
    )
    is_domestic_uae = fields.Boolean(
        string="Is Domestic UAE",
        readonly=True,
        default=False,
    )
    # Vendor data
    vendor_confirmation_number = fields.Char(
        string="Vendor Confirmation Number",
        required=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    manual_vendor_confirmation_number = fields.Char(
        string="Manual Vendor Confirmation Number",
        index=True,
        readonly=False,
        track_visibility='onchange',
    )
    vendor_name = fields.Char(
        string="Vendor Name",
        required=True,
        readonly=True,
        index=True,
    )
    vendor_currency_id = fields.Many2one(
        string="Vendor Currency",
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    vendor_cost_amount = fields.Monetary(
        string="Vendor Cost",
        currency_field='vendor_currency_id',
        readonly=True,
    )
    vendor_base_fare_amount = fields.Monetary(
        string="Vendor Base Fare",
        currency_field='vendor_currency_id',
        readonly=True,
    )
    vendor_input_tax_amount = fields.Monetary(
        string="Vendor Input Tax",
        currency_field='vendor_currency_id',
        readonly=True,
    )

    # Supplier data
    supplier_confirmation_number = fields.Char(
        string="Supplier Confirmation Number",
        required=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    manual_supplier_confirmation_number = fields.Char(
        string="Manual Supplier Confirmation Number",
        index=True,
        readonly=False,
        track_visibility='onchange',
    )
    supplier_name = fields.Char(
        string="Supplier Name",
        required=True,
        readonly=True,
        index=True,
    )
    supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    supplier_cost_amount = fields.Monetary(
        string="Supplier Cost",
        currency_field='supplier_currency_id',
        readonly=True,
    )
    supplier_base_fare_amount = fields.Monetary(
        string="Supplier Base Fare",
        currency_field='supplier_currency_id',
        readonly=True,
    )
    supplier_input_tax_amount = fields.Monetary(
        string="Supplier Input Tax",
        currency_field='supplier_currency_id',
        readonly=True,
    )
    exchange_rate = fields.Float(
        readonly=True,
    )

    # traveller details
    traveller = fields.Char(
        readonly=True,
    )
    traveller_type = fields.Char(
        string="Traveller type",
        readonly=True,
    )
    office_id = fields.Char(
        string="Office ID",
        readonly=True,
        index=True,
    )
    ticketing_office_id = fields.Char(
        string="Ticketing Office ID",
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    tour_code_office_id = fields.Char(
        string="Tour Code",
        readonly=True,
        index=True,
    )
    line_reference = fields.Char(
        string="Ticket/Segment",
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    manual_line_reference = fields.Char(
        string="Manual Ticket/Segment",
        indext=True,
        readonly=False,
        track_visibility='onchange',
    )
    tickets = fields.Char(
        string="Tickets",
        compute='_compute_tickets',
        readonly=True,
        store=False,
    )
    passengers_count = fields.Integer(
        string="Number of passengers",
        readonly=True,
    )
    last_leg_flying_date = fields.Char(
        string="Last LEG Flying date",
        readonly=True,
    )
    segment_count = fields.Integer(
        string="Number of Segments",
        readonly=True,
    )
    booking_class = fields.Char(
        string="Booking Class",
        readonly=True,
    )
    destination_city = fields.Char(
        string="Destination City",
        readonly=True,
    )
    departure_date = fields.Char(
        string="Departure Date",
        readonly=True,
    )
    route = fields.Char(
        string="Route",
        readonly=True,
    )
    origin_city = fields.Char(
        string="Origin City",
        readonly=True,
    )
    ahs_group_name = fields.Char(
        string="AHS Group Name",
        readonly=True,
    )
    validating_carrier = fields.Char(
        string="Validating Carrier",
        readonly=True,
    )
    hotel_name = fields.Char(
        string="Hotel Name",
        readonly=True,
    )
    total_supplier_price = fields.Monetary(
        string="Total Supplier Price",
        currency_field='supplier_currency_id',
        readonly=True,
    )
    # Segment details
    contract = fields.Char(
        string="Contract",
        readonly=True,
        track_visibility='onchange',
    )
    hotel_id = fields.Char(
        string="Hotel ID",
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    hotel_city = fields.Char(
        string="Hotel City",
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    hotel_country = fields.Char(
        string="Hotel Country",
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    hotel_supplier_id = fields.Char(
        string="Hotel Supplier ID",
        readonly=True,
    )
    check_in_date = fields.Datetime(
        string="Check In Date",
        readonly=True,
    )
    checkout_date = fields.Datetime(
        string="Check Out Date",
        readonly=True,
    )
    nb_nights = fields.Integer(
        string="No. of Nights",
        readonly=True,
    )
    nb_rooms = fields.Integer(
        string="No. of Rooms",
        readonly=True,
    )
    manual_checkout_date = fields.Datetime(
        string="Manual CheckOut Date",
        track_visibility='onchange',
    )
    manual_nb_nights = fields.Integer(
        string="Manual No. of Nights",
        track_visibility='onchange',
    )

    # Sale price data
    tax_code = fields.Selection(
        string="Tax Code",
        selection=[('ss', 'SS'), ('sz', 'SZ')],
        # TODO: mark readonly in live
        readonly=False,
        default='sz',
        required=True,
        # TODO update the help for the other cases.
        help="SS if the order is domestick KSA and Almsofer, else SZ",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    sale_price = fields.Monetary(
        string="Sale Price",
        currency_field='currency_id',
        readonly=True,
        help="Sale price = vendor cost + service fee.",
    )
    service_fee_amount = fields.Monetary(
        string="Service Fee",
        currency_field='currency_id',
        readonly=True,
        help="Prorated service fee",
    )
    discount_amount = fields.Monetary(
        string="Discount",
        currency_field='currency_id',
        readonly=True,
        help="Prorated discount amount",
    )
    tax_amount = fields.Monetary(
        string="Tax",
        currency_field='currency_id',
        readonly=True,
        help="Prorated tax amount",
    )
    subtotal_amount = fields.Monetary(
        string="Subtotal",
        currency_field='currency_id',
        readonly=True,
        help="Sale Price amount - discount amount"
    )
    total_amount = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        readonly=True,
        help="Total Amount = Sale Price amount + discount"
    )
    hub_bind_ids = fields.One2many(
        comodel_name='hub.sale.order.line',
        inverse_name='odoo_id',
        string="Hub Bindings",
        readonly=True,
    )
    matching_status = fields.Selection(
        string="Matching Status",
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable')],
        default='unmatched',
        required=True,
        index=True,
        readonly=True,
        track_visibility='onchange',
    )
    not_applicable_flag = fields.Char(
        string="Not applicable flag",
        index=True,
        readonly=True,
        track_visibility='onchange',
    )
    segments = fields.Char(
        string="Segments",
        readonly=True,
    )
    file_id = fields.Char(
        string="File Mongo ID",
        related='order_id.file_id',
    )
    file_reference = fields.Char(
        string="File ID",
        related='order_id.file_reference',
    )
    ticket_sub_type = fields.Char(
        string="Ticket Sub Type",
        related='order_id.ticket_sub_type',
    )
    is_unify = fields.Boolean(
        string="Is Unify",
        related='order_id.is_unify'
    )
    booking_category = fields.Selection(
        string="Is Amendment?",
        related='order_id.booking_category',
    )
    payment_request_reason = fields.Char(
        related='order_id.payment_request_reason',
    )
    payment_request_remarks = fields.Text(
        related='order_id.payment_request_remarks',
    )

    hotel_failed_reason = fields.Boolean(
        string="Hotel Skipped Lines",
        readonly=True,
        store=False,
        help="Technical field to serach hotel with has skipped as failing reason",
        search='_search_hotel_failed_reason_skipped',
    )

    @api.multi
    @api.depends('line_reference')
    def _compute_tickets(self):
        for rec in self:
            pass

    @api.multi
    @api.depends('line_reference', 'traveller', 'name')
    def name_get(self):
        result = []
        for rec in self:
            if rec.line_reference:
                result.append((rec.id, rec.line_reference))
                continue
            if rec.traveller:
                result.append((rec.id, rec.traveller))
                continue
            if rec.name:
                result.append((rec.id, rec.name))
                continue
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        connector = '|'
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            connector = '&'
        recs = self.search([connector, connector,
                            ('line_reference', operator, name),
                            ('traveller', operator, name),
                            ('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.model
    def _search_hotel_failed_reason_skipped(self, operator, value):
        if operator == '!=':
            return [('id', '=', 0)]

        self.env.cr.execute("""
            SELECT sale_order_id
            FROM ofh_sale_order_sap WHERE
                failing_reason='skipped' AND
                order_type='hotel';
            """)
        order_ids = [x[0] for x in self.env.cr.fetchall()]
        if not order_ids:
            return [('id', '=', 0)]

        return [('order_id', 'in', order_ids)]