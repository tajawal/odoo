# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import json


class OfhSaleOrderLineSap(models.Model):
    _name = 'ofh.sale.order.line.sap'
    _description = 'Ofh Sale Order Line SAP'
    _inherit = 'sap.binding'
    _order = 'id'

    send_date = fields.Datetime(
        string="Sending Date",
        required=True,
        readonly=True,
        index=True,
    )
    sale_order_line_id = fields.Many2one(
        string="Sale Order Line",
        comodel_name='ofh.sale.order.line',
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
    sap_sale_order_id = fields.Many2one(
        comodel_name='ofh.sale.order.sap',
        required=True,
        readonly=True,
        ondelete='cascade',
        index=True,
        auto_join=True
    )
    line_detail = fields.Text(
        string="Line Detail",
        readonly=True,
    )
    sap_line_detail = fields.Text(
        string="SAP Line Detail",
        readonly=True,
    )
    is_double_hoop = fields.Boolean(
        string="Is Double Hoop?",
        default=False,
        index=True,
    )
    # SAP Line Item Fields (Item General)
    booking_line_item_flag = fields.Char(  # sap_details
        string="Booking Line Item Flag",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    booking_line_item_number = fields.Char(  # sap_details
        string="Booking Line Item Number",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    line_item_billing_block = fields.Char(
        string="Line Item Billing Block",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    segment = fields.Char(
        string="Segment",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    service_item = fields.Char(
        string="Service Item",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    qty = fields.Char(
        string="Qty",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    billing_date = fields.Char(
        string="Billing Date",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    plant = fields.Char(
        string="Plant",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    vat_tax_code = fields.Char(
        string="VAT Tax Code",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    airline_code = fields.Char(
        string="Airline Code",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    iata_number = fields.Char(
        string="IATA Number",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    domestic_international = fields.Char(
        string="Domestic International",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    vendor = fields.Char(
        string="Vendor",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    vendor2 = fields.Char(
        string="Vendor2",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    travel_order_number = fields.Char(
        string="Travel Order Number",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    ticket_number = fields.Char(
        string="Ticket Number",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    pnr = fields.Char(
        string="PNR",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    gds_code = fields.Char(
        string="GDSCode",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    lcc_ind = fields.Char(
        string="LCCIND",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    vendor_confirmation = fields.Char(
        string="Vendor Confirmation",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    segment_count = fields.Char(
        string="Segment Count",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    custom1 = fields.Char(
        string="Custom1",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    pax_name = fields.Char(
        string="Pax Name",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    # SAP Sale Order Line Item fields (Item Characteristics)
    z_airlinecode = fields.Char(
        string="Z_AIRLINECODE",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_fare_class = fields.Char(
        string="Z_FARE_CLASS",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_booking_type = fields.Char(
        string="Z_BOOKING_TYPE",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_booking_class = fields.Char(
        string="Z_BOOKING_CLASS",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_lastlegflyingdate = fields.Char(
        string="Z_LASTLEGFLYINGDATE",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_paxname = fields.Char(
        string="Z_PAXNAME",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_vendor = fields.Char(
        string="Z_VENDOR",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_destinationcity = fields.Char(
        string="Z_DESTINATIONCITY",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_locater = fields.Char(
        string="Z_LOCATER",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_tktstatus = fields.Char(
        string="Z_TKTSTATUS",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_owneroid = fields.Char(
        string="Z_OWNEROID",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_departuredate = fields.Char(
        string="Z_DEPARTUREDATE",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_route = fields.Char(
        string="Z_ROUTE",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_iata = fields.Char(
        string="Z_IATA",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_numberofpax = fields.Char(
        string="Z_NUMBEROFPAX",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_seg1origin = fields.Char(
        string="Z_SEG1ORIGIN",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg1destination = fields.Char(
        string="Z_SEG1DESTINATION",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg2origin = fields.Char(
        string="Z_SEG2ORIGIN",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg2destination = fields.Char(
        string="Z_SEG2DESTINATION",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg3origin = fields.Char(
        string="Z_SEG3ORIGIN",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg3destination = fields.Char(
        string="Z_SEG3DESTINATION",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg4origin = fields.Char(
        string="Z_SEG4ORIGIN",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg4destination = fields.Char(
        string="Z_SEG4DESTINATION",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg5origin = fields.Char(
        string="Z_SEG5ORIGIN",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg5destination = fields.Char(
        string="Z_SEG5DESTINATION",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg6origin = fields.Char(
        string="Z_SEG6ORIGIN",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg6destination = fields.Char(
        string="Z_SEG6DESTINATION",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg7origin = fields.Char(
        string="Z_SEG7ORIGIN",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg7destination = fields.Char(
        string="Z_SEG7DESTINATION",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg8origin = fields.Char(
        string="Z_SEG8ORIGIN",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg8destination = fields.Char(
        string="Z_SEG8DESTINATION",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg9origin = fields.Char(
        string="Z_SEG9ORIGIN",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_seg9destination = fields.Char(
        string="Z_SEG9DESTINATION",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_suppliername_h = fields.Char(
        string="Z_SUPPLIERNAME_H",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_numberofnights = fields.Char(
        string="Z_NUMBEROFNIGHTS",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_numberofrooms = fields.Char(
        string="Z_NUMBEROFROOMS",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_startdate = fields.Char(
        string="Z_STARTDATE",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_checkout = fields.Char(
        string="Z_CHECKOUT",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_provider_h = fields.Char(
        string="Z_PROVIDER_H",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    z_serialnumber = fields.Char(
        string="Z_SERIALNUMBER",
        readonly=True,
        compute="_compute_sap_line_fields",
    )
    # SAP Sale Order Line Item fields (Item Conditions)
    zsel = fields.Char(
        string="ZSEL",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    zvd1 = fields.Char(
        string="ZVD1",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    zvnr = fields.Char(
        string="ZVNR",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    zvt1 = fields.Char(
        string="ZVT1",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    zgds = fields.Char(
        string="ZGDS",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    zdis = fields.Char(
        string="ZDIS",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    # Sale Order Line Fields (Item General)
    entity = fields.Selection(
        selection=[
            ('almosafer', 'Almosafer'),
            ('tajawal', 'Tajawal'),
            ('almosafer_branch', 'Almosafer Branch')],
        readonly=True,
        compute="_compute_line_fields"
    )
    order_number = fields.Char(
        string="Order Number",
        readonly=True,
        compute="_compute_line_fields"
    )
    item_type = fields.Char(
        string="Item Type",
        readonly=True,
        compute="_compute_line_fields"
    )
    order_status = fields.Char(
        string="order Status",
        readonly=True,
        compute="_compute_line_fields"
    )
    office_id = fields.Char(
        string="Office Id",
        readonly=True,
        compute="_compute_line_fields"
    )
    payment_status = fields.Char(
        string="Payment Status",
        readonly=True,
        compute="_compute_line_fields"
    )
    booking_method = fields.Char(
        string="Booking Method",
        readonly=True,
        compute="_compute_line_fields"
    )
    vendor_name = fields.Char(
        string="Vendor Name",
        readonly=True,
        compute="_compute_line_fields"
    )
    supplier_name = fields.Char(
        string="Supplier Name",
        readonly=True,
        compute="_compute_line_fields"
    )
    item_currency = fields.Char(
        string="Item Currency",
        readonly=True,
        compute="_compute_line_fields"
    )
    is_domestic_uae = fields.Boolean(
        string="Is Domestic UAE",
        readonly=True,
        default=False,
        compute="_compute_line_fields"
    )
    is_domestic_ksa = fields.Boolean(
        string="Is Domestic KSA",
        readonly=True,
        default=False,
        compute="_compute_line_fields"
    )
    ahs_group_name = fields.Char(
        string="Ahs Group Name",
        readonly=True,
        compute="_compute_line_fields"
    )
    number_of_pax = fields.Char(
        string="Number_Of Pax",
        readonly=True,
        compute="_compute_line_fields"
    )
    # Sale Order Line Fields (Item Characteristics)
    booking_class = fields.Char(
        string="airline_code",
        readonly=True,
        compute="_compute_line_fields"
    )
    last_leg_flying_date = fields.Date(
        string="booking_class",
        readonly=True,
        compute="_compute_line_fields"
    )
    destination_city = fields.Char(
        string="last_leg_flying_date",
        readonly=True,
        compute="_compute_line_fields"
    )
    departure_date = fields.Date(
        string="pax_name",
        readonly=True,
        compute="_compute_line_fields"
    )
    route = fields.Char(
        string="destination_city",
        readonly=True,
        compute="_compute_line_fields"
    )
    segments = fields.Char(
        string="order_status",
        readonly=True,
        compute="_compute_line_fields"
    )
    last_leg = fields.Char(
        string="departure_date",
        readonly=True,
        compute="_compute_line_fields"
    )
    # Sale Order Line Fields (Item Conditions)
    cost_currency = fields.Char(
        string="cost_currency",
        readonly=True,
        compute="_compute_line_fields"
    )
    currency = fields.Char(
        string="currency",
        readonly=True,
        compute="_compute_line_fields"
    )
    sale_price = fields.Char(
        string="sale_price",
        readonly=True,
        compute="_compute_line_fields"
    )
    cost_price = fields.Char(
        string="cost_price",
        readonly=True,
        compute="_compute_line_fields"
    )
    output_vat = fields.Char(
        string="output_vat",
        readonly=True,
        compute="_compute_line_fields"
    )
    discount = fields.Char(
        string="discount",
        readonly=True,
        compute="_compute_line_fields"
    )
    # Hotel details
    hotel_country = fields.Char(
        string="Hotel Country",
        readonly=True,
        compute="_compute_line_fields"
    )
    hotel_city = fields.Char(
        string="Hotel City",
        readonly=True,
        compute="_compute_line_fields"
    )
    hotel_id = fields.Char(
        string="Hotel Id",
        readonly=True,
        compute="_compute_line_fields"
    )
    hotel_supplier_id = fields.Char(
        string="Hotel Supplier Id",
        readonly=True,
        compute="_compute_line_fields"
    )
    hotel_contract_name = fields.Char(
        string="Hotel Contract Name",
        readonly=True,
        compute="_compute_line_fields"
    )
    failing_text = fields.Char(
        string="Response",
        readonly=True,
        store=False,
        related='sap_sale_order_id.failing_text',
    )
    track_id = fields.Char(
        string="Track Id",
        readonly=True,
        store=False,
        compute="_compute_track_id"
    )
    created_at = fields.Datetime(
        string="Order Creation Date",
        readonly=True,
        store=False,
        related='sap_sale_order_id.sale_order_id.created_at',
    )
    hotel_name = fields.Char(
        string="Hotel Name",
        readonly=True,
        store=False,
        related='sale_order_line_id.hotel_name',
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    @api.multi
    @api.depends('line_detail')
    def _compute_line_fields(self):
        for rec in self:
            if rec.line_detail:
                line_detail = json.loads(rec.line_detail)
            else:
                line_detail = {}
            rec.entity = line_detail.get('entity')
            rec.order_number = line_detail.get('order_number')
            rec.item_type = line_detail.get('item_type')
            rec.order_status = line_detail.get('order_status')
            rec.office_id = line_detail.get('office_id')
            rec.payment_status = line_detail.get('payment_status')
            rec.booking_method = line_detail.get('booking_method')
            rec.vendor_name = line_detail.get('vendor_name')
            rec.supplier_name = line_detail.get('supplier_name')
            rec.item_currency = line_detail.get('item_currency')
            rec.is_domestic_uae = line_detail.get('is_domestic_uae')
            rec.is_domestic_ksa = line_detail.get('is_domestic_ksa')
            rec.ahs_group_name = line_detail.get('ahs_group_name')
            rec.number_of_pax = line_detail.get('number_of_pax')
            rec.booking_class = line_detail.get('booking_class')
            rec.last_leg_flying_date = line_detail.get('last_leg_flying_date')
            rec.destination_city = line_detail.get('destination_city')
            rec.departure_date = line_detail.get('departure_date')
            rec.route = line_detail.get('route')
            rec.segments = line_detail.get('segments')
            rec.last_leg = line_detail.get('last_leg')
            rec.cost_currency = line_detail.get('cost_currency')
            rec.currency = line_detail.get('currency')
            rec.sale_price = line_detail.get('sale_price')
            rec.cost_price = line_detail.get('cost_price')
            rec.output_vat = line_detail.get('output_vat')
            rec.discount = line_detail.get('discount')
            rec.hotel_country = line_detail.get('hotel_country')
            rec.hotel_city = line_detail.get('hotel_city')
            rec.hotel_id = line_detail.get('hotel_id')
            rec.hotel_supplier_id = line_detail.get('hotel_supplier_id')
            rec.hotel_contract_name = line_detail.get('hotel_contract_name')

    @api.multi
    @api.depends('sap_line_detail')
    def _compute_sap_line_fields(self):
        for rec in self:
            if rec.sap_line_detail:
                sap_line_detail = json.loads(rec.sap_line_detail)
            else:
                sap_line_detail = {}

            rec.booking_line_item_flag = sap_line_detail.get(
                'BookingLineItemFlag')
            rec.booking_line_item_number = sap_line_detail.get(
                'BookingLineitemNumber')
            rec.line_item_billing_block = sap_line_detail.get(
                'LineItemBillingBlock')
            rec.segment = sap_line_detail.get('Segment')
            rec.service_item = sap_line_detail.get('ServiceItem')
            rec.qty = sap_line_detail.get('Qty')
            rec.billing_date = sap_line_detail.get('BillingDate')
            rec.plant = sap_line_detail.get('Plant')
            rec.vat_tax_code = sap_line_detail.get('VATTaxCode')
            rec.airline_code = sap_line_detail.get('AirlineCode')
            rec.iata_number = sap_line_detail.get('IATANumber')
            rec.domestic_international = sap_line_detail.get(
                'DomesticInternational')
            rec.vendor = sap_line_detail.get('Vendor')
            rec.vendor2 = sap_line_detail.get('Vendor2')
            rec.travel_order_number = sap_line_detail.get('TravelOrderNumber')
            rec.ticket_number = sap_line_detail.get('TicketNumber')
            rec.pnr = sap_line_detail.get('PNR')
            rec.gds_code = sap_line_detail.get('GDSCode')
            rec.lcc_ind = sap_line_detail.get('LCCIND')
            rec.vendor_confirmation = sap_line_detail.get('VendorConfirmation')
            rec.segment_count = sap_line_detail.get('SegmentCount')
            rec.custom1 = sap_line_detail.get('Custom1')
            rec.pax_name = sap_line_detail.get('Pax_Name')

            for charac in sap_line_detail.get('ItemCharecteristics', []):
                rec[charac.get('CharecteristicName').lower()] = \
                    charac.get('Value')

            for cond in sap_line_detail.get('Conditions', []):
                rec[cond.get('ConditionType').lower()] = \
                    f"{cond.get('Value')} {cond.get('Currency')}"

    @api.multi
    @api.depends('sap_sale_order_id', 'payment_request_id')
    def _compute_track_id(self):
        for rec in self:
            if rec.sap_sale_order_id:
                rec.track_id = rec.sap_sale_order_id.sale_order_id.track_id
            elif rec.payment_request_id:
                rec.track_id = rec.payment_request_id.track_id

    @api.multi
    def action_mark_order_as_not_applicable(self):
        sales = self.filtered(
            lambda r: r.sap_sale_order_id.sale_order_id).mapped(
                'sap_sale_order_id.sale_order_id')
        if sales:
            sales.action_sale_not_applicable()
        prs = self.filtered(
            lambda r: r.payment_request_id).mapped(
                'payment_request_id')
        if prs:
            prs.action_sale_not_applicable()
