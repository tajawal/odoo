# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class HubPaymentRequestImporter(Component):

    _inherit = 'hub.payment.request.importer'

    def _must_block(self, binding) -> str:
        """Must block binding from being updated."""
        # if binding.new_sap_status:
        #     return 'Synchronization is blocked order '\
        #         'has already been sent to SAP.'
        return ''
