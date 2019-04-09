# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OfhPaymentCharge(models.Model):
    _name = 'ofh.payment.charge'
    _description = "Ofh Payment Charge"
    _rec_name = 'charge_id'

    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    created_at = fields.Datetime(
        required=True,
        index=True,
        readonly=True,
    )
    updated_at = fields.Datetime(
        required=True,
        index=True,
        readonly=True,
        track_visibility='always',
    )
    charge_id = fields.Char(
        string="Charge Id",
        required=True,
        readonly=True,
        index=True,
    )
    track_id = fields.Char(
        string="Track Id",
        required=True,
        readonly=True,
        index=True,
    )
    auth_code = fields.Char(
        string="Auth Code",
        required=True,
        readonly=True,
        index=True,
    )
    status = fields.Char(
        string="Status",
        required=True,
        readonly=True,
        index=True,
    )
    currency = fields.Char(
        string="Currency",
        required=True,
        readonly=True,
        index=True,
    )
    total = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        required=True,
        readonly=True,
        index=True,
    )
    provider = fields.Char(
        string="Provider",
        required=True,
        readonly=True,
        index=True,
    )
    payment_mode = fields.Char(
        string="Payment Mode",
        readonly=True,
        index=True,
    )
    card_type = fields.Char(
        string="Card Type",
        readonly=True,
        index=True,
    )
    mid = fields.Char(
        string="Mid",
        readonly=True,
        index=True,
    )
    last_four = fields.Char(
        string="Last Four",
        readonly=True,
        index=True,
    )
    card_bin = fields.Char(
        string="Card Bin",
        readonly=True,
        index=True,
    )
