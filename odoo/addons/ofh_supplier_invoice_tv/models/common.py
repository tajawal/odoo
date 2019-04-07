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
        return {'locator': record.get('SupplierConfirmation')}

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
        dt = datetime.strptime(record.get('OrderDate'), '%Y-%m-%dT%H:%M:%S.%f')
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
    def supplier_currency(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return {}
        supplier_curr = record.get('SupplierCurrency')
        if not supplier_curr:
            return {}
        return {'supplier_currency': supplier_curr}

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
            return super(SupplierInvoiceLineMapper, self).invoice_status(record)
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
        offc_id = record.get('ServiceType')
        if not offc_id:
            return {}
        return {'office_id': offc_id}

    @mapping
    def index(self, record):
        tv_backend = self.env.ref(
            'ofh_supplier_invoice_tv.tv_import_backend')
        if self.backend_record != tv_backend:
            return {}
        return {'index': record.get('OrderId')}


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
