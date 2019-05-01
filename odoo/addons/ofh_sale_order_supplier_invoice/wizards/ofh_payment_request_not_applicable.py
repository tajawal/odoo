# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OfhSaleOrderLineNot_applicable(models.TransientModel):

    _name = 'ofh.payment.request.not_applicable'

    @api.model
    def _get_default_payment_request_ids(self):
        active_model = self.env.context.get('active_model')
        if active_model != 'ofh.payment.request':
            raise ValidationError(
                _("The active model is not the one expected."))
        active_ids = self.env.context.get('active_ids', [])
        return self.env[active_model].browse(active_ids)

    payment_request_ids = fields.Many2many(
        comodel_name='ofh.payment.request',
        relation='ofh_payment_request_not_applicable_rel',
        column1='wizard_id',
        column2='order_id',
        default=_get_default_payment_request_ids,
    )
    not_applicable_flag = fields.Char(
        string="Reason",
        required=True,
    )

    @api.multi
    def action_matching_status_not_applicable(self):
        self.ensure_one()
        self.payment_request_ids.action_matching_status_not_applicable(
            not_applicable_flag=self.not_applicable_flag)
