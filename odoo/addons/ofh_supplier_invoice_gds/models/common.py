# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from datetime import datetime

from odoo import fields
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SupplierInvoiceLineGDSMapper(Component):
    _name = 'supplier.invoice.line.gds.mapper'
    _inherit = 'importer.base.mapper'
    _apply_on = 'ofh.supplier.invoice.line'

    required = {
        'Record locator': 'locator',
        'Date': 'invoice_date',
    }

    defaults = [
        ('invoice_type', 'gds'),
    ]

    direct = [
        ("Passenger's name", 'passenger'),
        ('Total', 'total'),
        ('Airline Code', 'vendor_id'),
        ('Record locator', 'locator'),
        ('Office ID', 'office_id'),
        ('Ticket number', 'ticket_number'),
        ('GDS ticket status', 'invoice_status')
    ]

    @mapping
    def invoice_date(self, record):
        dt = datetime.strptime(record.get('Date'), '%d/%m/%y')
        return {'invoice_date': fields.Date.to_string(dt)}

    @mapping
    def fees(self, record):
        fees = {
            'Base fare': record.get('Base fare', 0.0),
            'Tax': record.get('Tax', 0.0),
            'Net': record.get('Net', 0.0),
            'Fee': record.get('Fee', 0.0),
            'IATA commission': record.get('IATA commission', 0.0),
        }
        return {'fees': json.dumps(fees)}

    @mapping
    def invoice_status(self, record):
        status = record.get('GDS ticket status')
        if not status:
            return {}
        if status in ('EMDA', 'EMDS'):
            status = 'AMND'
        return {'invoice_status': status}


class SupplierInvoiceLineGDSRecordImporter(Component):

    _name = 'supplier.invoice.line.gds.record.importer'
    _inherit = 'importer.record'
    _apply_on = ['ofh.supplier.invoice.line']

    odoo_unique_key = 'name'

    def required_keys(self, create=False):
        """Keys that are mandatory to import a line."""
        return {}


class SupplierInvoiceLineGDSHandler(Component):
    _inherit = 'importer.odoorecord.handler'
    _name = 'supplier.invoice.line.handler'
    _apply_on = ['ofh.supplier.invoice.line']

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the record in odoo."""
        return [
            ('invoice_type', '=', 'gds'),
            (self.unique_key, '=', 'gds_{}{}'.format(
                values.get('Ticket number'), values.get('GDS ticket status')))]
