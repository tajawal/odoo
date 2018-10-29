# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class HubImportMapper(AbstractComponent):
    _name = 'hub.import.mapper'
    _inherit = ['base.hub.connector', 'base.import.mapper']
    _usage = 'import.mapper'
