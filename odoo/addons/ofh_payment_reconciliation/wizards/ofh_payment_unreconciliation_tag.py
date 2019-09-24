# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OfhPaymentUnReconciliationTag(models.TransientModel):
    _name = 'ofh.payment.unreconciliation.tag'

    @api.model
    def _get_default_payment_ids(self):
        active_model = self.env.context.get('active_model')
        if active_model != 'ofh.payment':
            raise ValidationError(
                _("The active model is not the one expected."))
        active_ids = self.env.context.get('active_ids', [])
        return self.env[active_model].browse(active_ids)

    payment_ids = fields.Many2many(
        comodel_name='ofh.payment',
        relation='payment_unreconciliation_rel',
        column1='wizard_id',
        column2='payment_id',
        default=_get_default_payment_ids,
    )
    unreconciliation_tag = fields.Char(
        string="Unreconciliation Reason",
        required=True,
    )

    @api.multi
    def action_update_unreconciliation_tag(self):
        self.ensure_one()
        self.payment_ids.action_update_unreconciliation_tag(
            unreconciliation_tag=self.unreconciliation_tag)
