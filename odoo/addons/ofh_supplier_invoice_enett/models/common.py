# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SupplierInvoiceLineMapper(Component):
    _inherit = 'supplier.invoice.line.mapper'

    @mapping
    def ticket_number(self, record):
        enett_backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')
        if self.backend_record != enett_backend:
            return super(SupplierInvoiceLineMapper, self).ticket_number(record)
        ticket_num = record.get('Ticket No')
        if not ticket_num:
            return {}
        return {'ticket_number': ticket_num}

    @mapping
    def invoice_type(self, record):
        enett_backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')
        if self.backend_record != enett_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_type(record)
        return {'invoice_type': 'enett'}

    @mapping
    def locator(self, record):
        enett_backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')
        if self.backend_record != enett_backend:
            return super(SupplierInvoiceLineMapper, self).locator(record)
        return {'locator': record.get('Ticket No')}

    @mapping
    def vendor_id(self, record):
        enett_backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')
        if self.backend_record != enett_backend:
            return super(SupplierInvoiceLineMapper, self).vendor_id(record)
        hn = record.get('Merch. Name')
        if not hn:
            return {}
        return {'vendor_id': hn}

    @mapping
    def invoice_date(self, record):
        enett_backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')
        if self.backend_record != enett_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_date(record)
        dt = datetime.strptime(record.get('Date'), '%m/%d/%Y')
        if not dt:
            return {}
        return {'invoice_date': dt}

    @mapping
    def currency_id(self, record):
        enett_backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')
        if self.backend_record != enett_backend:
            return super(SupplierInvoiceLineMapper, self).currency_id(record)
        currency = record.get('POS Settle Curr')
        if not currency:
            return {}
        return {'currency_id': self.env.ref('base.' + currency).id}

    @mapping
    def passenger(self, record):
        enett_backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')
        if self.backend_record != enett_backend:
            return super(SupplierInvoiceLineMapper, self).passenger(record)
        passeng = record.get('Customer Name')
        if not passeng:
            return {}
        return {'passenger': passeng}

    @mapping
    def invoice_status(self, record):
        enett_backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')
        if self.backend_record != enett_backend:
            return super(SupplierInvoiceLineMapper, self) \
                .invoice_status(record)
        return {'invoice_status': 'TKTT'}

    @mapping
    def office_id(self, record):
        enett_backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')
        if self.backend_record != enett_backend:
            return super(SupplierInvoiceLineMapper, self).office_id(record)
        return {'office_id': "Travel Fusion"}

    @mapping
    def order_reference(self, record):
        enett_backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')
        if self.backend_record != enett_backend:
            return super(SupplierInvoiceLineMapper, self) \
                .order_reference(record)
        return {'order_reference': record.get('Tajawal ID')}

    @mapping
    def total(self, record):
        enett_backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')
        if self.backend_record != enett_backend:
            return super(SupplierInvoiceLineMapper, self).total(record)

        return {'total': float(record.get('POS Settle Amt'))}


class SupplierInvoiceLineHandler(Component):
    _inherit = 'supplier.invoice.line.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the Enett invoice line record in odoo."""
        enett_backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')
        if self.backend_record == enett_backend:
            return [
                ('invoice_type', '=', 'enett'),
                (self.unique_key, '=', 'enett_{}_{}'.format(
                    values.get('Tajawal ID'),
                    values.get('Ticket No')))]
        return super(SupplierInvoiceLineHandler, self).odoo_find_domain(
            values, orig_values)
