# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from datetime import datetime

from odoo import api, fields, models
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector_importer.models.job_mixin import JobRelatedMixin


class SupplierInvoiceLineMapper(Component):
    _inherit = 'supplier.invoice.line.mapper'

    @mapping
    def invoice_date(self, record):
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_date(record)
        dt = datetime.strptime(record.get('Date'), '%m/%d/%Y')
        return {'invoice_date': fields.Date.to_string(dt)}

    @mapping
    def fees(self, record):
        fees = {
            'BaseFare': record.get("Base fare", 0.0),
            'Tax': record.get('Tax', 0.0),
            'Net': record.get('Net', 0.0),
            'FEE': record.get('FEE', 0.0),
            'IATA COMM': record.get("IATA commission", 0.0),
        }
        return {'fees': json.dumps(fees)}

    @mapping
    def invoice_status(self, record):
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(
                SupplierInvoiceLineMapper, self).invoice_status(record)
        status = record.get('GDS ticket status')
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
        return {'passenger': record.get("Passenger's name")}

    @mapping
    def office_id(self, record):
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).office_id(record)
        return {'office_id': record.get('Office ID')}

    @mapping
    def ticket_number(self, record):
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).ticket_number(record)
        return {'ticket_number': record.get("Ticket number")}

    @mapping
    def locator(self, record):
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).locator(record)
        return {'locator': record.get("Record locator")}

    @mapping
    def vendor_id(self, record):
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).vendor_id(record)
        return {'vendor_id': record.get("Airline Code")}

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

    @mapping
    def currency_id(self, record):
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).currency_id(record)
        office = record.get("Office ID")
        if not office:
            return {}
        office = office.upper()
        if office.startswith('R'):
            return {'currency_id': self.env.ref('base.SAR').id}
        elif office.startswith('K'):
            return {'currency_id': self.env.ref('base.KWD').id}
        elif office.startswith('C'):
            return {'currency_id': self.env.ref('base.EGP').id}
        else:
            return {}


class ImportRecordSet(models.Model, JobRelatedMixin):
    _inherit = 'import.recordset'

    @api.multi
    def run_import(self):
        self.ensure_one()
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_id == gds_backend:
            return self._run_import(channel='root.import.gds')
        return super(ImportRecordSet, self).run_import()


class ImportRecord(models.Model, JobRelatedMixin):
    _inherit = 'import.record'

    @api.multi
    def run_import(self):
        self.ensure_one()
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_id == gds_backend:
            return self._run_import(channel='root.import.gds')
        return super(ImportRecord, self).run_import()


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
