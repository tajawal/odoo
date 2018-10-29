# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseHubConnectorComponent(AbstractComponent):

    _name = 'base.hub.connector'
    _inherit = 'base.connector'
    _collection = 'hub.backend'
