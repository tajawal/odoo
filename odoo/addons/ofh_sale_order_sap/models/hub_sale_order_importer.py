# Copyright 2019 Tajawa LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class HubSaleOrderImporter(Component):

    _inherit = 'hub.sale.order.importer'

    def _must_block(self, binding) -> str:
        """Must block binding from being updated."""
        if binding.sap_status:
            return 'Synchronization is blocked order '\
                'has already been sent to SAP.'
        return ''
