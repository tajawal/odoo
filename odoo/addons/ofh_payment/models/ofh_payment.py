# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
    )
    updated_at = fields.Datetime(
        required=True,
        readonly=True,
        track_visibility='always',
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    total_amount = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        readonly=True,
    )
    payment_mode = fields.Char(
        string="Payment Method",
        readonly=True,
    )
    payment_status = fields.Selection(
        string="Payment Status",
        selection=_get_payment_status_selection,
        required=False,
        readonly=True,
    )
    provider = fields.Char(
        string="Provider",
        readonly=True,
        index=True,
    )
    source = fields.Char(
        string="Source",
        readonly=True,
        index=True,
    )
    charge_ids = fields.One2many(
        comodel_name="ofh.payment.charge",
        string="Charge IDs",
        inverse_name='payment_id',
        readonly=True,
    )
    track_id = fields.Char(
        string="Track Id",
        required=True,
        readonly=True,
        index=True,
    )
    auth_code = fields.Char(
        string="Auth Code",
        readonly=True,
    )
    card_type = fields.Char(
        string="Card Type",
        readonly=True,
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
    payment_method = fields.Char(
        string="Payment method",
        readonly=True,
    )
    bank_name = fields.Char(
        string="Bank name",
        readonly=True,
    )
    source = fields.Char(
        string="Source",
        readonly=True,
    )
    reference_id = fields.Char(
        string="Reference ID",
        readonly=True,
    )
    is_3d_secure = fields.Boolean(
        string="Is 3d Secure",
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
