# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.addons.component.core import Component
from datetime import datetime


class HubSaleOrder(models.Model):
    _name = 'hub.sale.order'
    _inherit = 'hub.binding'
    _inherits = {'ofh.sale.order': 'odoo_id'}

    odoo_id = fields.Many2one(
        comodel_name='ofh.sale.order',
        string='Order',
        required=True,
        ondelete='cascade',
    )
    hub_line_ids = fields.One2many(
        comodel_name='hub.sale.order.line',
        inverse_name='hub_order_id',
        string="Hub Order Lines",
    )

    _sql_constraints = [
        ('hub_uniq', 'unique(backend_id, external_id)',
         _("A binding already exists with the same Hub ID.")),
    ]


class HubSaleOrderLine(models.Model):
    _name = 'hub.sale.order.line'
    _inherit = 'hub.binding'
    _inherits = {'ofh.sale.order.line': 'odoo_id'}

    odoo_id = fields.Many2one(
        comodel_name='ofh.sale.order.line',
        string='Order',
        required=True,
        ondelete='cascade',
    )
    hub_order_id = fields.Many2one(
        string="HUB Sale order",
        comodel_name='hub.sale.order',
        required=True,
        ondelete='cascade',
        index=True,
    )

    @api.model
    def create(self, vals):
        hub_order_id = vals['hub_order_id']
        binding = self.env['hub.sale.order'].browse(hub_order_id)
        vals['order_id'] = binding.odoo_id.id
        binding = super(HubSaleOrderLine, self).create(vals)
        return binding


class SaleOrderAdapter(Component):

    _name = 'ofh.sale.order.adapter'
    _inherit = 'hub.adapter'
    _apply_on = 'hub.sale.order'

    def search(self, filters: dict) -> list:
        try:
            hub_api = getattr(self.work, 'hub_api')
        except AttributeError:
            raise AttributeError(
                'You must provide a hub_api attribute with a '
                'HubAPI instance to be able to use the '
                'Backend Adapter.'
            )
        from_date = filters.pop('from')
        if not from_date:
            from_date = datetime.strptime("2018-09-01", "%Y-%m-%d")
        to_date = filters.pop('to')
        if not to_date:
            to_date = datetime.now()
        return hub_api.get_list_order(from_date=from_date, to_date=to_date)

    def read(self, external_id, attributes={}) -> dict:
        try:
            hub_api = getattr(self.work, 'hub_api')
        except AttributeError:
            raise AttributeError(
                'You must provide a hub_api attribute with a '
                'HubAPI instance to be able to use the '
                'Backend Adapter.'
            )
        return hub_api.get_raw_order(external_id)
