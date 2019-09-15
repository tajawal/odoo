# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OfhBankSettlement(models.Model):
    _inherit = 'ofh.bank.settlement'

    payment_gateway_id = fields.Many2one(
        string="Payment Gateway Id",
        comodel_name='ofh.payment.gateway',
        required=False,
        ondelete='cascade'
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
        track_visibility='always',
    )
