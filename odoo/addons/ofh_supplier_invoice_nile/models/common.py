# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SupplierInvoiceLineMapper(Component):
    _inherit = 'supplier.invoice.line.mapper'

    @mapping
    def ticket_number(self, record):
        nile_backend = self.env.ref(
            'ofh_supplier_invoice_nile.nile_import_backend')
        if self.backend_record != nile_backend:
            return super(SupplierInvoiceLineMapper, self).ticket_number(record)
        segment_id = record.get('Ticket Number')
        if not segment_id:
            return {}
        return {'ticket_number': segment_id}

    @mapping
    def invoice_type(self, record):
        nile_backend = self.env.ref(
            'ofh_supplier_invoice_nile.nile_import_backend')
        if self.backend_record != nile_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_type(record)
        return {'invoice_type': 'nile'}

    @mapping
    def locator(self, record):
        nile_backend = self.env.ref(
            'ofh_supplier_invoice_nile.nile_import_backend')
        if self.backend_record != nile_backend:
            return super(SupplierInvoiceLineMapper, self).locator(record)
        return {'locator': record.get('GDS PNR')}

    @mapping
    def vendor_id(self, record):
        nile_backend = self.env.ref(
            'ofh_supplier_invoice_nile.nile_import_backend')
        if self.backend_record != nile_backend:
            return super(SupplierInvoiceLineMapper, self).vendor_id(record)
        return {'vendor_id': "Nile Air"}

    @mapping
    def invoice_date(self, record):
        nile_backend = self.env.ref(
            'ofh_supplier_invoice_nile.nile_import_backend')
        if self.backend_record != nile_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_date(record)
        dt = datetime.strptime(record.get('TKT Issue Date'), '%d-%b-%y')
        if not dt:
            return {}
        return {'invoice_date': dt}

    @mapping
    def currency_id(self, record):
        nile_backend = self.env.ref(
            'ofh_supplier_invoice_nile.nile_import_backend')
        if self.backend_record != nile_backend:
            return super(SupplierInvoiceLineMapper, self).currency_id(record)
        return {'currency_id': self.env.ref('base.SAR').id}

    @mapping
    def passenger(self, record):
        nile_backend = self.env.ref(
            'ofh_supplier_invoice_nile.nile_import_backend')
        if self.backend_record != nile_backend:
            return super(SupplierInvoiceLineMapper, self).passenger(record)
        passeng = record.get('Pax Name')
        if not passeng:
            return {}
        return {'passenger': passeng}

    @mapping
    def invoice_status(self, record):
        nile_backend = self.env.ref(
            'ofh_supplier_invoice_nile.nile_import_backend')
        if self.backend_record != nile_backend:
            return super(SupplierInvoiceLineMapper, self) \
                .invoice_status(record)
        return {'invoice_status': "TKTT"}

    @mapping
    def gds_net_amount(self, record):
        nile_backend = self.env.ref(
            'ofh_supplier_invoice_nile.nile_import_backend')
        if self.backend_record != nile_backend:
            return {}
        return {'gds_net_amount': record.get('Amount Due')}

    @mapping
    def order_reference(self, record):
        itl_backend = self.env.ref(
            'ofh_supplier_invoice_itl.itl_import_backend')
        if self.backend_record != itl_backend:
            return {}
        return {'order_reference': record.get('Order ID')}


class SupplierInvoiceLineHandler(Component):
    _inherit = 'supplier.invoice.line.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the nile invoice line record in odoo."""
        nile_backend = self.env.ref(
            'ofh_supplier_invoice_nile.nile_import_backend')
        if self.backend_record == nile_backend:
            return [
                ('invoice_type', '=', 'nile'),
                (self.unique_key, '=', 'nile_{}_{}'.format(
                    values.get('Order ID'),
                    values.get('Ticket Number')))]
        return super(SupplierInvoiceLineHandler, self).odoo_find_domain(
            values, orig_values)
