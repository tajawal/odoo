# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from hashlib import blake2b

from odoo import fields
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SupplierInvoiceLineMapper(Component):
    _inherit = 'supplier.invoice.line.mapper'

    @mapping
    def invoice_date(self, record):
        tf_backend = self.env.ref(
           'ofh_supplier_invoice_tf.tf_import_backend')
        if self.backend_record != tf_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_type(record)
        dt = datetime.strptime(record.get('Date'), '%m/%d/%y')
        return {'invoice_date': fields.Date.to_string(dt)}

    @mapping
    def invoice_type(self, record):
        tf_backend = self.env.ref(
           'ofh_supplier_invoice_tf.tf_import_backend')
        if self.backend_record != tf_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_type(record)
        return {'invoice_type': 'tf'}

    @mapping
    def currency_id(self, record) -> dict:
        tf_backend = self.env.ref(
           'ofh_supplier_invoice_tf.tf_import_backend')
        if self.backend_record != tf_backend:
            return super(SupplierInvoiceLineMapper, self).currency_id(record)
        return {
            'currency_id': self.env.ref(
                'base.{}'.format(record.get('Currency'))).id}

    @mapping
    def invoice_status(self, record):
        tf_backend = self.env.ref(
           'ofh_supplier_invoice_tf.tf_import_backend')
        if self.backend_record != tf_backend:
            return super(SupplierInvoiceLineMapper, self).invoice_status(
                record)
        if record.get('Payment amount'):
            return {'invoice_status': 'TKTT'}
        elif record.get('Refund amount'):
            return {'invoice_status': 'RFND'}

    @mapping
    def total(self, record):
        return {
            'total': max(
                record.get('Payment amount'), record.get('Refund amount'))
        }

    @mapping
    def passenger(self, record):
        tf_backend = self.env.ref(
           'ofh_supplier_invoice_tf.tf_import_backend')
        if self.backend_record != tf_backend:
            return super(SupplierInvoiceLineMapper, self).passenger(record)
        return {'passenger': record.get("Passenger's name")}

    @mapping
    def vendor_id(self, record):
        tf_backend = self.env.ref(
           'ofh_supplier_invoice_tf.tf_import_backend')
        if self.backend_record != tf_backend:
            return super(SupplierInvoiceLineMapper, self).passenger(record)
        return {'vendor_id': record.get('Airline')}

    @mapping
    def locator(self, record):
        tf_backend = self.env.ref(
           'ofh_supplier_invoice_tf.tf_import_backend')
        if self.backend_record != tf_backend:
            return super(SupplierInvoiceLineMapper, self).locator(record)
        return {'locator': record.get('Airline PNR')}


class SupplierInvoiceLineHandler(Component):
    _inherit = 'supplier.invoice.line.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the Travelfusion invoice line record in odoo."""
        tf_backend = self.env.ref(
           'ofh_supplier_invoice_tf.tf_import_backend')
        if self.backend_record != tf_backend:
            return super(SupplierInvoiceLineHandler, self).odoo_find_domain(
                values, orig_values)

        uniq_ref = f"{values.get('locator')}{values.get('passenger')}" \
                   f"{values.get('invoice_date')}{values.get('total')}"
        uniq_ref = blake2b(key=str.encode(uniq_ref), digest_size=9).hexdigest()

        return [
            ('invoice_type', '=', 'tf'),
            (self.unique_key, '=', 'tf_{}'.format(uniq_ref))]
