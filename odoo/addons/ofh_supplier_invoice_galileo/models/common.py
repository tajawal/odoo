# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SupplierInvoiceLineMapper(Component):
    _inherit = 'supplier.invoice.line.mapper'

    @mapping
    def ticket_number(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self).ticket_number(record)
        segment_id = record.get('Ticket Number')
        if not segment_id:
            return {}
        return {'ticket_number': segment_id}

    @mapping
    def invoice_type(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_type(record)
        return {'invoice_type': 'galileo'}

    @mapping
    def locator(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self).locator(record)
        return {'locator': record.get('PNR')}

    @mapping
    def vendor_id(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self).vendor_id(record)
        hn = record.get('Airline Numeric')
        if not hn:
            return {}
        return {'vendor_id': hn}

    @mapping
    def invoice_date(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_date(record)
        dt = datetime.strptime(record.get('Issued'), '%m/%d/%Y')
        if not dt:
            return {}
        return {'invoice_date': dt}

    @mapping
    def total(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self).total(record)
        supplier_pr = record.get('Total')
        if not supplier_pr:
            return {}
        return {'total': supplier_pr}

    @mapping
    def supplier_reference(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self)\
                .supplier_reference(record)
        supplier_ref = record.get('SupplierReference')
        if not supplier_ref:
            return {}
        return {'supplier_reference': supplier_ref}

    @mapping
    def currency_id(self, record):
        gds_backend = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_backend')
        if self.backend_record != gds_backend:
            return super(SupplierInvoiceLineMapper, self).currency_id(record)
        currency = record.get('Currency')
        if not currency:
            return {}
        return {'currency_id': self.env.ref('base.' + currency).id}

    @mapping
    def passenger(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self).passenger(record)
        passeng = record.get('Passenger')
        if not passeng:
            return {}
        return {'passenger': passeng}

    @mapping
    def invoice_status(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self)\
                .invoice_status(record)
        invoice_stat = record.get('Type')
        if not invoice_stat:
            return {}
        return {'invoice_status': invoice_stat}

    @mapping
    def office_id(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self).office_id(record)
        offc_id = record.get('PCC')
        if not offc_id:
            return {}
        return {'office_id': offc_id}

    @mapping
    def gds_net_amount(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self)\
                .gds_net_amount(record)
        return {'gds_net_amount': record.get('Amount Due')}

    @mapping
    def gds_net_amount(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self)\
                .gds_net_amount(record)
        return {'gds_net_amount': record.get('Amount Due')}

    @mapping
    def gds_base_fare_amount(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self)\
                .gds_base_fare_amount(record)
        return {'gds_base_fare_amount': record.get('Base Fare')}

    @mapping
    def gds_iata_commission_amount(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self)\
                .gds_iata_commission_amount(record)
        return {'gds_iata_commission_amount': record.get('Commission')}

    @mapping
    def gds_tax_amount(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self)\
                .gds_tax_amount(record)
        return {'gds_tax_amount': record.get('Tax')}

    @mapping
    def gds_fee_amount(self, record):
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record != galileo_backend:
            return super(SupplierInvoiceLineMapper, self)\
                .gds_fee_amount(record)
        return {'gds_fee_amount': record.get('Fee')}


class SupplierInvoiceLineHandler(Component):
    _inherit = 'supplier.invoice.line.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the galileo invoice line record in odoo."""
        galileo_backend = self.env.ref(
            'ofh_supplier_invoice_galileo.galileo_import_backend')
        if self.backend_record == galileo_backend:
            return [
                ('invoice_type', '=', 'galileo'),
                (self.unique_key, '=', 'galileo_{}_{}'.format(
                    values.get('Ticket Number'),
                    values.get('PCC')))]
        return super(SupplierInvoiceLineHandler, self).odoo_find_domain(
            values, orig_values)
