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
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record != tp_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_date(record)
        dt = datetime.strptime(record.get('Issued'), '%m/%d/%Y')
        return {'invoice_date': fields.Date.to_string(dt)}

    @mapping
    def fees(self, record):
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record != tp_backend:
            return super(SupplierInvoiceLineMapper, self).fees(record)
        base_fare = record.get('Base Fare', 0.0)
        tax = record.get('Tax', 0.0)
        if not tax:
            tax = 0.0
        fees = {
            'BaseFare': base_fare,
            'Tax': tax,
            'FEE': record.get('Fee', 0.0),
            'Net': float(base_fare) + float(tax),
            'IATA COMM': record.get("Commission", 0.0)
        }
        return {'fees': json.dumps(fees)}

    @mapping
    def invoice_status(self, record):
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record != tp_backend:
            return super(
                SupplierInvoiceLineMapper, self).invoice_status(record)
        status = record.get('Type')
        if not status:
            status = 'TKTT'
        elif status == 'XA - Exchange':
            status = 'AMND'
        elif status == 'RF - Refund':
            status = 'RFND'
        return {'invoice_status': status}

    @mapping
    def passenger(self, record):
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record != tp_backend:
            return super(SupplierInvoiceLineMapper, self).passenger(record)
        return {'passenger': record.get("Passenger")}

    @mapping
    def office_id(self, record):
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record != tp_backend:
            return super(SupplierInvoiceLineMapper, self).office_id(record)
        return {'office_id': record.get('PCC')}

    @mapping
    def ticket_number(self, record):
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record != tp_backend:
            return super(SupplierInvoiceLineMapper, self).ticket_number(record)
        return {'ticket_number': record.get("Ticket Number")}

    @mapping
    def locator(self, record):
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record != tp_backend:
            return super(SupplierInvoiceLineMapper, self).locator(record)
        return {'locator': record.get("PNR")}

    @mapping
    def vendor_id(self, record):
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record != tp_backend:
            return super(SupplierInvoiceLineMapper, self).vendor_id(record)
        return {'vendor_id': record.get("Airline Numeric")}

    @mapping
    def total(self, record):
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record != tp_backend:
            return super(SupplierInvoiceLineMapper, self).total(record)
        return {'total': record.get('Amount Due')}

    @mapping
    def invoice_type(self, record):
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record != tp_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_type(record)
        return {'invoice_type': 'tp'}

    @mapping
    def agent_sign_in(self, record):
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record != tp_backend:
            return super(SupplierInvoiceLineMapper, self).agent_sign_in(record)
        return {'agent_sign_in': record.get('SON')}
    @mapping
    def currency_id(self, record):
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record != tp_backend:
            return super(SupplierInvoiceLineMapper, self).currency_id(record)
        currency = record.get("Currency")
        return {'currency_id': self.env.ref("base."+currency).id}


class ImportRecordSet(models.Model, JobRelatedMixin):
    _inherit = 'import.recordset'

    @api.multi
    def run_import(self):
        self.ensure_one()
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_id == tp_backend:
            return self._run_import(channel='root.import.tp')
        return super(ImportRecordSet, self).run_import()


class ImportRecord(models.Model, JobRelatedMixin):
    _inherit = 'import.record'

    @api.multi
    def run_import(self):
        self.ensure_one()
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_id == tp_backend:
            return self._run_import(channel='root.import.tp')
        return super(ImportRecord, self).run_import()


class SupplierInvoiceLineHandler(Component):
    _inherit = 'supplier.invoice.line.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the TravelPort invoice line record in odoo."""
        tp_backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        if self.backend_record == tp_backend:
            return [
                ('invoice_type', '=', 'tp'),
                (self.unique_key, '=', 'tp_{}{}'.format(
                    values.get('Ticket number'),
                    values.get('TravelPort ticket status')))]
        return super(SupplierInvoiceLineHandler, self).odoo_find_domain(
            values, orig_values)


class SupplierInvoiceLineRecordImporter(Component):

    _inherit = 'supplier.invoice.line.record.importer'

    def skip_it(self, values, origin_values) -> dict:
        """ Return True if the response code does not starts with 1.

        Arguments:
            values {dict} -- Mapped values
            origin_values {dict} -- Original raw data.
        """
        status = origin_values.get('Status', '')

        if status not in ('', 'XA - Exchange', 'RF - Refund'):
            return {'message': "This TravelPort invoice not applicable for import"}
        return {}
