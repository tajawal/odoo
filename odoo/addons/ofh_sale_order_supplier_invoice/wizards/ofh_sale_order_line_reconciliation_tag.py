# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OfhSaleOrderLineReconciliationTag(models.TransientModel):

    _name = 'ofh.sale.order.line.reconciliation.tag'

    name = fields.Char()

    @api.model
    def _get_default_line_ids(self):
        active_model = self.env.context.get('active_model')
        if active_model not in ('ofh.sale.order.line', 'ofh.sale.order'):
            raise ValidationError(
                _("The active model is not the one expected."))
        active_ids = self.env.context.get('active_ids', [])
        if active_model == 'ofh.sale.order.line':
            return self.env[active_model].browse(active_ids)
        else:
            return self.env[active_model].browse(active_ids).mapped('line_ids')

    line_ids = fields.Many2many(
        comodel_name='ofh.sale.order.line',
        relation='ofh_sale_order_line_reconciliation_rel',
        column1='wizard_id',
        column2='line_id',
        default=_get_default_line_ids,
    )
    reconciliation_tag = fields.Char(
        string="Investigation Tag",
        required=True,
    )

    @api.multi
    @api.constrains('line_ids')
    def _check_line_ids(self):
        for rec in self:
            if rec.line_ids.filtered(lambda l: l.matching_status != 'matched'):
                raise ValidationError(_(
                    "You can't put a reconciliation tag in unmatched lines."))

    @api.multi
    def action_update_reconciliation_tag(self):
        self.ensure_one()
        self.line_ids.action_update_reconciliation_tag(
            reconciliation_tag=self.reconciliation_tag)
