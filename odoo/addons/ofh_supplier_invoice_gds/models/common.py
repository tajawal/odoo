# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from datetime import datetime

from odoo import fields
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SupplierInvoiceLineMapper(Component):
    _inherit = 'supplier.invoice.line.mapper'

    @mapping
    def invoice_date(self, record):
        gds_backend = self.env.ref(
           'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(
                SupplierInvoiceLineMapper, self).invoice_status(record)
        dt = datetime.strptime(record.get('Date'), '%d/%m/%y')
        return {'invoice_date': fields.Date.to_string(dt)}

    @mapping
    def fees(self, record):
        fees = {
            'BaseFare': record.get('BaseFare', 0.0),
            'Tax': record.get('Tax', 0.0),
            'Net': record.get('Net', 0.0),
            'FEE': record.get('FEE', 0.0),
            'IATA COMM': record.get('IATA COMM', 0.0),
        }
        return {'fees': json.dumps(fees)}

    @mapping
    def invoice_status(self, record):
        gds_backend = self.env.ref(
           'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(
                SupplierInvoiceLineMapper, self).invoice_status(record)
        status = record.get('Tkt Status')
        if not status:
            return {}
        if status in ('EMDA', 'EMDS'):
            status = 'AMND'
        return {'invoice_status': status}

    @mapping
    def passenger(self, record):
        gds_backend = self.env.ref(
           'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).passenger(record)
        return {'passenger': record.get("PAX Name")}

    @mapping
    def office_id(self, record):
        gds_backend = self.env.ref(
           'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).office_id(record)
        return {'office_id': record.get('OwnerOID')}

    @mapping
    def ticket_number(self, record):
        gds_backend = self.env.ref(
           'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).ticket_number(record)
        return {'ticket_number': record.get('DocNumber')}

    @mapping
    def locator(self, record):
        gds_backend = self.env.ref(
           'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).locator(record)
        return {'locator': record.get('Locater')}

    @mapping
    def vendor_id(self, record):
        gds_backend = self.env.ref(
           'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).vendor_id(record)
        return {'vendor_id': record.get('Air Line')}

    @mapping
    def total(self, record):
        gds_backend = self.env.ref(
           'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).total(record)
        return {'total': record.get('Total')}

    @mapping
    def invoice_type(self, record):
        gds_backend = self.env.ref(
           'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_type(record)
        return {'invoice_type': 'gds'}


class SupplierInvoiceLineHandler(Component):
    _inherit = 'supplier.invoice.line.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the GDS invoice line record in odoo."""
        gds_backend = self.env.ref(
           'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record == gds_backend:
            return [
                ('invoice_type', '=', 'gds'),
                (self.unique_key, '=', 'gds_{}{}'.format(
                    values.get('Ticket number'), 
                    values.get('GDS ticket status')))]
        return super(SupplierInvoiceLineHandler, self).odoo_find_domain(
            values, orig_values)
