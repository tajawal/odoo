# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OfhSaleOrderLine(models.TransientModel):

    _name = 'ofh.sale.order.line.investigation.tag'

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
        relation='ofh_sale_order_line_investigation_rel',
        column1='wizard_id',
        column2='line_id',
        default=_get_default_line_ids,
    )
    investigation_tag = fields.Char(
        string="Investigation Tag",
        required=True,
    )

    @api.multi
    def action_update_investigation_tag(self):
        self.ensure_one()
        self.line_ids.action_update_investigation_tag(
            investigation_tag=self.investigation_tag)
