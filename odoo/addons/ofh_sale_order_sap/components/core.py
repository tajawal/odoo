# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseSapConnectorComponent(AbstractComponent):

    _name = 'base.sap.connector'
    _inherit = 'base.connector'
    _collection = 'sap.backend'
