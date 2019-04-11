# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SupplierInvoiceLineMapper(Component):
    _inherit = 'supplier.invoice.line.mapper'

    @mapping
    def ticket_number(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self).ticket_number(record)
        segment_id = record.get('Ticket No.')
        if not segment_id:
            return {}
        return {'ticket_number': segment_id}

    @mapping
    def invoice_type(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_type(record)
        return {'invoice_type': 'itl'}

    @mapping
    def vendor_id(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self).vendor_id(record)
        return {'vendor_id': "ITL"}

    @mapping
    def invoice_date(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_date(record)
        dt = datetime.strptime(record.get('Date'), '%d-%b-%Y')
        if not dt:
            return {}
        return {'invoice_date': dt}

    @mapping
    def currency_id(self, record):
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).currency_id(record)
        return {'currency_id': self.env.ref('base.AED').id}

    @mapping
    def passenger(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self).passenger(record)
        passeng = record.get('PAX Name')
        if not passeng:
            return {}
        return {'passenger': passeng}\

    @mapping
    def total(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self).total(record)
        totl = record.get('Ticket Total')
        if not totl:
            return {}
        return {'total': totl}

    @mapping
    def invoice_status(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self) \
                .invoice_status(record)
        net_payable = record.get('Ticket Total')
        if float(net_payable) >= 0:
            return {'invoice_status': "TKTT"}
        return {'invoice_status': "RFND"}

    @mapping
    def office_id(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self).office_id(record)
        return {'office_id': "ITL"}

    @mapping
    def locator(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self).locator(record)
        return {'locator': "/"}

    @mapping
    def gds_fee_amount(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return {}
        return {'gds_fee_amount': float(record.get('S/F'))}

    @mapping
    def gds_base_fare_amount(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return {}
        return {'gds_base_fare_amount': float(record.get('Fare'))}

    @mapping
    def gds_tax_amount(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return {}
        return {'gds_tax_amount': float(record.get('Tax'))}

    @mapping
    def order_reference(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self) \
                .order_reference(record)
        return {'order_reference': record.get('LPO No.')}


class SupplierInvoiceLineHandler(Component):
    _inherit = 'supplier.invoice.line.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the itl invoice line record in odoo."""
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record == itl_backend:
            return [
                ('invoice_type', '=', 'itl'),
                (self.unique_key, '=', 'itl_{}_{}'.format(
                    values.get('LPO No.'),
                    values.get('Ticket No.')))]
        return super(SupplierInvoiceLineHandler, self).odoo_find_domain(
            values, orig_values)
