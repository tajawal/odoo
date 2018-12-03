# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import fields
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SupplierInvoiceLineMapper(Component):
    _inherit = 'supplier.invoice.line.mapper'

    @mapping
    def invoice_date(self, record):
        aig_backend = self.env.ref(
            'ofh_supplier_invoice_aig.aig_import_backend')
        if self.backend_record != aig_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_date(record)
        if not record.get('ISSUE DATE'):
            return {}
        dt = datetime.strptime(record.get('ISSUE DATE'), '%d-%b-%y')
        return {'invoice_date': fields.Date.to_string(dt)}

    @mapping
    def invoice_status(self, record):
        aig_backend = self.env.ref(
            'ofh_supplier_invoice_aig.aig_import_backend')
        if self.backend_record != aig_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_status(
                record)
        status = record.get('STATUS')
        if not status:
            return {}
        if status == 'Sold':
            return {'invoice_status': 'TKTT'}
        elif status == 'Cancelled':
            return {'invoice_status': 'RFND'}
        return {}

    @mapping
    def passenger(self, record):
        aig_backend = self.env.ref(
            'ofh_supplier_invoice_aig.aig_import_backend')
        if self.backend_record != aig_backend:
            return super(SupplierInvoiceLineMapper, self).passenger(record)
        return {'passenger': record.get('INSURED NAME')}

    @mapping
    def vendor_id(self, record):
        aig_backend = self.env.ref(
            'ofh_supplier_invoice_aig.aig_import_backend')
        if self.backend_record != aig_backend:
            return super(SupplierInvoiceLineMapper, self).vendor_id(record)
        return {'vendor_id': 'AIG'}

    @mapping
    def office_id(self, record):
        aig_backend = self.env.ref(
            'ofh_supplier_invoice_aig.aig_import_backend')
        if self.backend_record != aig_backend:
            return super(SupplierInvoiceLineMapper, self).office_id(record)
        return {}

    @mapping
    def locator(self, record):
        aig_backend = self.env.ref(
            'ofh_supplier_invoice_aig.aig_import_backend')
        if self.backend_record != aig_backend:
            return super(SupplierInvoiceLineMapper, self).locator(record)
        return {'locator': record.get('POLICY NUMBER')}

    @mapping
    def ticket_number(self, record):
        aig_backend = self.env.ref(
            'ofh_supplier_invoice_aig.aig_import_backend')
        if self.backend_record != aig_backend:
            return super(SupplierInvoiceLineMapper, self).ticket_number(record)
        return {'ticket_number': record.get('VOUCHER NUMBER')}

    @mapping
    def total(self, record):
        aig_backend = self.env.ref(
            'ofh_supplier_invoice_aig.aig_import_backend')
        if self.backend_record != aig_backend:
            return super(SupplierInvoiceLineMapper, self).total(record)
        return {'total': record.get('TOTAL PREMIUM')}

    @mapping
    def invoice_type(self, record):
        aig_backend = self.env.ref(
            'ofh_supplier_invoice_aig.aig_import_backend')
        if self.backend_record != aig_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_type(record)
        return {'invoice_type': 'aig'}

    @mapping
    def currency_id(self, record):
        aig_backend = self.env.ref(
            'ofh_supplier_invoice_aig.aig_import_backend')
        if self.backend_record != aig_backend:
            return super(SupplierInvoiceLineMapper, self).currency_id(record)
        currency = record.get('CURRENCY')
        if not currency:
            return {}
        return {'currency_id': self.env.ref('base.{}'.format(currency)).id}


class SupplierInvoiceLineHandler(Component):
    _inherit = 'supplier.invoice.line.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the Travelfusion invoice line record in odoo."""
        aig_backend = self.env.ref(
            'ofh_supplier_invoice_aig.aig_import_backend')
        if self.backend_record != aig_backend:
            return super(SupplierInvoiceLineHandler, self).odoo_find_domain(
                values, orig_values)
        uniq_ref = \
            f"{values.get('ticket_number')}{values.get('invoice_status')}"
        return [
            ('invoice_type', '=', 'aig'),
            (self.unique_key, '=', 'aig_{}'.format(uniq_ref))]
