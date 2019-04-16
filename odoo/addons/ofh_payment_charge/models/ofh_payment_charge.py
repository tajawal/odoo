# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhPaymentCharge(models.Model):
    _name = 'ofh.payment.charge'
    _description = "Ofh Payment Charge"
    _rec_name = 'charge_id'
    _order = 'created_at DESC'

    @api.model
    def _get_charge_status_selection(self):
        return [
            ("11111", "Captured"), ("83027", "Refund"),
            ("83026", "Refund In Progress"), ("83025", "Refund Failed"),
            ("00000", "Declined"), ("10000", "Authorized"),
            ("20118", "Pending"), ("83035", "Void"), ("99999", "Deleted"),
            ("10100", "Flagged")
        ]

    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    created_at = fields.Datetime(
        required=True,
        readonly=True,
    )
    updated_at = fields.Datetime(
        required=True,
        readonly=True,
        track_visibility='always',
    )
    charge_id = fields.Char(
        string="Charge Id",
        required=True,
        readonly=True,
    )
    track_id = fields.Char(
        string="Track Id",
        required=True,
        readonly=True,
    )
    auth_code = fields.Char(
        string="Auth Code",
        readonly=True,
    )
    status = fields.Selection(
        string="Status",
        selection=_get_charge_status_selection,
        required=True,
        readonly=True,
    )
    total = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        readonly=True,
    )
    provider = fields.Char(
        string="Provider",
        readonly=True,
    )
    payment_mode = fields.Char(
        string="Payment Mode",
        readonly=True,
    )
    card_type = fields.Char(
        string="Card Type",
        readonly=True,
    )
    mid = fields.Char(
        string="Mid",
        readonly=True,
    )
    last_four = fields.Char(
        string="Last Four",
        readonly=True,
    )
    card_bin = fields.Char(
        string="Card Bin",
        readonly=True,
    )
