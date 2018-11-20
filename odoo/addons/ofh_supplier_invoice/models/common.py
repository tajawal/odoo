# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SupplierInvoiceLineMapper(Component):
    _name = 'supplier.invoice.line.mapper'
    _inherit = 'importer.base.mapper'
    _apply_on = 'ofh.supplier.invoice.line'

    @mapping
    def invoice_date(self, record):
        return {}

    @mapping
    def invoice_status(self, record):
        return {}

    @mapping
    def passenger(self, record):
        return {}

    @mapping
    def vendor_id(self, record):
        return {}

    @mapping
    def office_id(self, record):
        return {}

    @mapping
    def locator(self, record):
        return {}

    @mapping
    def ticket_number(self, record):
        return {}

    @mapping
    def total(self, record):
        return {}

    @mapping
    def invoice_type(self, record):
        return {}

    @mapping
    def currency_id(self, record):
        return {}


class SupplierInvoiceLineRecordImporter(Component):

    _name = 'supplier.invoice.line.record.importer'
    _inherit = 'importer.record'
    _apply_on = ['ofh.supplier.invoice.line']

    odoo_unique_key = 'name'

    def required_keys(self, create=False):
        """Keys that are mandatory to import a line."""
        return {}


class SupplierInvoiceLineHandler(Component):
    _inherit = 'importer.odoorecord.handler'
    _name = 'supplier.invoice.line.handler'
    _apply_on = ['ofh.supplier.invoice.line']
