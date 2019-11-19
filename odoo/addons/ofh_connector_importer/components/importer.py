# Author: Simone Orsi
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component

class RecordImporter(Component):

    _inherit = 'importer.record'

    def _do_report(self):
        """Update recordset report using the tracker in a separate job"""
        previous = self.recordset.get_report()
        report = self.tracker.get_report(previous)
        self.recordset.with_delay().set_report({self.model._name: report})
