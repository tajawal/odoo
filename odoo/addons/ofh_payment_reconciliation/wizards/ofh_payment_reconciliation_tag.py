# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OfhPaymentReconciliationTag(models.TransientModel):
    _name = 'ofh.payment.reconciliation.tag'

    @api.model
    def _get_default_payment_gateway_ids(self):
        active_model = self.env.context.get('active_model')
        if active_model != 'ofh.payment.gateway':
            raise ValidationError(
                _("The active model is not the one expected."))
        active_ids = self.env.context.get('active_ids', [])
        return self.env[active_model].browse(active_ids)

    payment_gateway_ids = fields.Many2many(
        comodel_name='ofh.payment.gateway',
        relation='payment_gateway_reconciliation_rel',
        column1='wizard_id',
        column2='payment_gateway_id',
        default=_get_default_payment_gateway_ids,
    )
    reconciliation_tag = fields.Char(
        string="Investigation Tag",
        required=True,
    )

    @api.multi
    def action_update_reconciliation_tag(self):
        self.ensure_one()
        self.payment_gateway_ids.action_update_reconciliation_tag(
            reconciliation_tag=self.reconciliation_tag)
