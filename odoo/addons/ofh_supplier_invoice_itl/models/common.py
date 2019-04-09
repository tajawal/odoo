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
        segment_id = record.get('Ticket Number')
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
    def locator(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self).locator(record)
        return {'locator': record.get('PNR')}

    @mapping
    def vendor_id(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self).vendor_id(record)
        hn = record.get('Airline Name')
        if not hn:
            return {}
        return {'vendor_id': hn}

    @mapping
    def invoice_date(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_date(record)
        dt = datetime.strptime(record.get('Date'), '%Y-%m-%d')
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
        passeng = record.get('Passenger Name')
        if not passeng:
            return {}
        return {'passenger': passeng}

    @mapping
    def invoice_status(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self) \
                .invoice_status(record)
        net_payable = record.get('Net Payable')
        if int(net_payable) >= 0:
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
    def gds_net_amount(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return {}
        return {'gds_net_amount': float(record.get('Net Payable'))}

    @mapping
    def gds_base_fare_amount(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return {}
        return {'gds_base_fare_amount': float(record.get('Basic Fare'))}

    @mapping
    def gds_tax_amount(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return {}
        return {'gds_tax_amount': float(record.get('Taxes'))}

    @mapping
    def order_reference(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return super(SupplierInvoiceLineMapper, self) \
                .order_reference(record)
        return {'order_reference': record.get('Tajawal ID')}


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
                    values.get('Tajawal ID'),
                    values.get('Ticket Number')))]
        return super(SupplierInvoiceLineHandler, self).odoo_find_domain(
            values, orig_values)
