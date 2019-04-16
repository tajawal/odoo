# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class HubModelBinder(Component):
    """Bind records and give odoo/hub ids correspondence
    Binding models are models called ``hub.{model_name}``,
    like ``hub.payment.request`` or ``hub.sale.order``
    Arguments:
        Component {[type]} -- [description]
    """

    _name = 'hub.binder'
    _inherit = ['base.binder', 'base.hub.connector']

    _apply_on = [
        'hub.payment.request',
        'hub.sale.order',
        'hub.sale.order.line',
        'hub.payment.charge',
        'hub.payment',
    ]
