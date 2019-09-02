# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector_importer.models.job_mixin import JobRelatedMixin


class SupplierInvoiceLineMapper(Component):
    _inherit = 'supplier.invoice.line.mapper'

    @mapping
    def ticket_number(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return super(SupplierInvoiceLineMapper, self).ticket_number(record)
        segment_id = record.get('SegmentId')
        if not segment_id:
            return {}
        return {'ticket_number': segment_id}

    @mapping
    def invoice_type(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_type(record)
        return {'invoice_type': 'tv'}

    @mapping
    def locator(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return super(SupplierInvoiceLineMapper, self).locator(record)
        return {'locator': record.get('OrderId')}

    @mapping
    def vendor_id(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return super(SupplierInvoiceLineMapper, self).vendor_id(record)
        hn = record.get('HotelName')
        if not hn:
            return {}
        return {'vendor_id': hn}

    @mapping
    def invoice_date(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_date(record)
        dt = datetime.strptime(record.get('OrderDate'), '%Y-%m-%d')
        if not dt:
            return {}
        return {'invoice_date': dt}

    @mapping
    def total(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return super(SupplierInvoiceLineMapper, self).total(record)
        supplier_pr = record.get('PriceInSupplierCurrency')
        if not supplier_pr:
            return {}
        return {'total': supplier_pr}

    @mapping
    def supplier_reference(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return {}
        supplier_ref = record.get('SupplierReference')
        if not supplier_ref:
            return {}
        return {'supplier_reference': supplier_ref}

    @mapping
    def currency_id(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return super(SupplierInvoiceLineMapper, self).currency_id(record)
        currency = record.get("SupplierCurrency")
        if not currency:
            return {'currency_id': self.env.ref('base.SAR').id}
        return {'currency_id': self.env.ref(f'base.{currency}').id}

    @mapping
    def passenger(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return super(SupplierInvoiceLineMapper, self).passenger(record)
        passeng = record.get('LeadPax')
        if not passeng:
            return {}
        return {'passenger': passeng}

    @mapping
    def invoice_status(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_status(
                record)
        invoice_stat = record.get('SegmentStatus')
        if not invoice_stat or invoice_stat != "OK":
            return {}
        return {'invoice_status': 'TKTT'}

    @mapping
    def office_id(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return super(SupplierInvoiceLineMapper, self).office_id(record)
        return {'office_id': "Hotel"}

    @mapping
    def index(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return super(SupplierInvoiceLineMapper, self).index(record)
        return {'index': record.get('OrderId')}

    @mapping
    def booked_by_branch(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return {}
        return {'booked_by_branch': record.get('BookedByBranch')}

    @mapping
    def booked_by_user(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return {}
        return {'booked_by_user': record.get('BookedByUser')}


class ImportRecordSet(models.Model, JobRelatedMixin):
    _inherit = 'import.recordset'

    @api.multi
    def run_import(self):
        self.ensure_one()
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_id == gds_backend:
            return self._run_import(channel='root.import.tv')
        return super(ImportRecordSet, self).run_import()


class ImportRecord(models.Model, JobRelatedMixin):
    _inherit = 'import.record'

    @api.multi
    def run_import(self):
        self.ensure_one()
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_id == gds_backend:
            return self._run_import(channel='root.import.tv')
        return super(ImportRecord, self).run_import()


class SupplierInvoiceLineHandler(Component):
    _inherit = 'supplier.invoice.line.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the TV invoice line record in odoo."""
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record == tv_backend:
            return [
                ('invoice_type', '=', 'tv'),
                (self.unique_key, '=', 'tv_{}_{}'.format(
                    values.get('OrderId'),
                    values.get('SegmentId')))]
        return super(SupplierInvoiceLineHandler, self).odoo_find_domain(
            values, orig_values)
