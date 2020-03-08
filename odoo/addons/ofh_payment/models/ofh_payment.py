# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.queue_job.job import job


class OfhPayment(models.Model):
    _name = 'ofh.payment'
    _description = "Ofh Payment"
    _rec_name = 'track_id'

    @api.model
    def _get_payment_status_selection(self):
        return self.env['ofh.payment.charge']._get_charge_status_selection()

    created_at = fields.Datetime(
        required=True,
        readonly=True,
        index=True,
    )
    updated_at = fields.Datetime(
        required=True,
        readonly=True,
        track_visibility='always',
        index=True,
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True,
        readonly=True,
        index=True,
    )
    total_amount = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        readonly=True,
    )
    payment_status = fields.Selection(
        string="Payment Status",
        selection=_get_payment_status_selection,
        required=False,
        readonly=True,
    )
    provider = fields.Selection(
        string="Provider",
        selection=[
            ('checkoutcom', 'Checkout'),
            ('fort', 'Fort'),
            ('knet', 'Knet'),
            ('qitaf', 'Qitaf'),
            ('wallet', 'Wallet'),
            ('tp', 'Tajawal Pay'),
            ('not_applicable', 'Not Applicable'), ],
        readonly=True,
        index=True,
    )
    source = fields.Char(
        string="Source",
        readonly=True,
        index=True,
    )
    charge_ids = fields.One2many(
        string="Charge IDs",
        comodel_name="ofh.payment.charge",
        inverse_name='payment_id',
        readonly=True,
    )
    track_id = fields.Char(
        string="Track Id",
        required=True,
        readonly=True,
        index=True,
    )
    track_ids = fields.Char(
        string="Track IDs",
        compute='_compute_track_id',
        search='_search_track_id',
        store=False,
        readonly=True,
    )
    auth_code = fields.Char(
        string="Auth Code",
        readonly=True,
        index=True,
    )
    card_type = fields.Selection(
        string="Card Type",
        selection=[
            ('visa', 'Visa'),
            ('amex', 'Amex'),
            ('mastercard', 'MasterCard'),
            ('not_applicable', 'Not Applicable')],
        readonly=True,
        index=True,
    )
    mid = fields.Char(
        string="MID",
        readonly=True,
    )
    card_name = fields.Char(
        string="Card Name",
        readonly=True,
    )
    card_bin = fields.Char(
        string="Card BIN",
        readonly=True,
    )
    last_four = fields.Char(
        string="Last Four",
        readonly=True,
    )
    payment_method = fields.Selection(
        string="Payment Method",
        readonly=True,
        selection=[
            ('online', 'Online'),
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('loyalty', 'Loyalty'),
            ('span', 'SPAN/POS'),
        ],
        index=True,
    )
    bank_name = fields.Char(
        string="Bank name",
        readonly=True,
    )
    reference_id = fields.Char(
        string="Reference ID",
        readonly=True,
    )
    is_installment = fields.Boolean(
        string="Is Installment",
        readonly=True,
    )
    hub_bind_ids = fields.One2many(
        comodel_name='hub.payment',
        inverse_name='odoo_id',
        string="Hub Bindings",
        readonly=True,
    )
    booking_source = fields.Selection(
        string="Booking Source",
        selection=[
            ('offline', 'Offline'),
            ('online', 'Online')],
        readonly=True,
        store=True,
        compute="_compute_booking_source"
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
    payment_category = fields.Selection(
        selection=[
            ('charge', 'Charge'),
            ('refund', 'Refund')],
        index=True,
        readonly=True,
    )
    rrn_no = fields.Char(
        string="RRN NO.",
        readonly=True,
    )
    iban = fields.Char(
        string="IBAN",
        readonly=True,
    )
    cashier_id = fields.Char(
        string="Branch Cashier ID",
        readonly=True,
    )
    successfactors_id = fields.Char(
        string="Successfactors ID",
        readonly=True,
    )
    ahs_group_name = fields.Char(
        string="AHS Group Name",
        readonly=True,
        index=True,
    )
    is_apple_pay = fields.Boolean(
        string="Is Apple Pay?",
        readonly=True,
        default=False,
    )
    is_mada = fields.Boolean(
        string="Is Mada?",
        readonly=True,
        default=False,
    )
    is_3d_secure = fields.Boolean(
        string="Is 3d Secure?",
        readonly=True,
        default=False,
    )
    store_id = fields.Char(
        string="Store ID",
        readonly=True,
        index=True,
    )
    parent_track_id = fields.Char(
        string="Parent Track ID",
        readonly=True,
        compute="_compute_parent_track_id",
        search="_search_parent_track_id",
    )

    @api.model
    def _search_track_id(self, operator, value):
        if operator == 'ilike':
            ids = value.replace(" ", "").split(",")
            return [('track_id', 'in', ids)]
        return [('track_id', operator, value)]

    @api.multi
    @api.depends('track_id')
    def _compute_track_id(self):
        for rec in self:
            rec.track_ids = rec.track_id

    @api.multi
    @api.depends('charge_ids.track_id', 'payment_category')
    def _compute_parent_track_id(self):
        for rec in self:
            if rec.charge_ids and rec.payment_category == "refund":
                rec.parent_track_id = rec.charge_ids[0].track_id

    @api.model
    def _search_parent_track_id(self, operator, value):
        if operator == 'ilike':
            ids = value.replace(" ", "").split(",")
            return [('charge_ids.track_id', 'in', ids)]
        return [('charge_ids.track_id', operator, value)]

    @api.multi
    @api.depends('track_id')
    def _compute_booking_source(self):
        for rec in self:
            track_id = rec.track_id
            rec.booking_source = 'online'
            if track_id.find('mp') != -1:
                rec.booking_source = 'offline'
                continue

    @job(default_channel='root.hub')
    @api.multi
    def action_update_hub_data(self):
        self.ensure_one()
        if self.order_id.booking_category:
            payment_type = self.order_id.booking_category
        elif self.payment_category == 'refund':
            payment_type = 'refund'
        else:
            payment_type = 'amendment'

        return self.hub_bind_ids.import_record(
            backend=self.hub_bind_ids.backend_id,
            external_id=self.track_id,
            payment_type=payment_type,
            force=True)

    @api.multi
    def open_payment_in_hub(self):
        """Open the order link to the payment request in hub using URL
        Returns:
            [dict] -- URL action dictionary
        """

        self.ensure_one()
        hub_backend = self.env['hub.backend'].search([], limit=1)
        if not hub_backend:
            return

        hub_url = ''
        if self.file_id:
            hub_url = "{}admin/unify/file/{}".format(
                hub_backend.hub_api_location, self.file_id)
        elif self.order_id:
            hub_url = "{}admin/order/air/detail/{}".format(
                hub_backend.hub_api_location, self.order_id.name)

        return {
            "type": "ir.actions.act_url",
            "url": hub_url,
            "target": "new",
        }
