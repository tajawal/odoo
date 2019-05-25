# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class SAPModelBinder(Component):

    _name = 'sap.binder'
    _inherit = ['base.binder', 'base.sap.connector']

    _apply_on = [
        'ofh.sale.order.sap',
        'ofh.sale.order.line.sap',
        'ofh.payment.sap',
    ]
