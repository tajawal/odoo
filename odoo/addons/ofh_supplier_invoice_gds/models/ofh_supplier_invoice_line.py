# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from datetime import datetime

from odoo import api, fields, models
from odoo.addons.queue_job.job import job


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    invoice_type = fields.Selection(
        selection_add=[('gds', 'GDS')],
    )
    gds_base_fare_amount = fields.Monetary(
        string="Base Fare",
        compute='_compute_fees',
        currency_field='currency_id',
    )
    gds_tax_amount = fields.Monetary(
        string="Tax",
        compute='_compute_fees',
        currency_field='currency_id',
    )
    gds_net_amount = fields.Monetary(
        string="Net",
        compute='_compute_fees',
        currency_field='currency_id',
    )
    gds_fee_amount = fields.Monetary(
        string="Fee",
        compute='_compute_fees',
        currency_field='currency_id',
    )
    gds_iata_commission_amount = fields.Monetary(
        string="IATA Commission",
        compute='_compute_fees',
        currency_field='currency_id',
    )
    invoice_status = fields.Selection(
        selection_add=[
            ('TKTT', 'Ticket'),
            ('AMND', 'Amendment'),
            ('RFND', 'Refund')],
    )

    @api.multi
    def _gds_compute_name(self):
        self.ensure_one
        self.name = '{}_{}{}'.format(
            self.invoice_type, self.ticket_number, self.invoice_status)

    @api.multi
    def _gds_compute_fees(self, fees: dict) -> None:
        self.ensure_one()
        if not fees:
            self.gds_base_fare_amount = self.gds_tax_amount = \
                self.gds_net_amount = \
                self.gds_fee_amount = self.gds_iata_commission_amount = 0.0
        else:
            self.gds_base_fare_amount = fees.get('Base fare', 0.0)
            self.gds_tax_amount = fees.get('Tax', 0.0)
            self.gds_net_amount = fees.get('Net', 0.0)
            self.gds_fee_amount = fees.get('FEE', 0.0)
            self.gds_iata_commission_amount = fees.get('IATA commission', 0.0)

    @job(default_channel='root')
    @api.model
    def import_gds_batch(self, records):
        """Import GDS batch report."""
        if not records:
            return False
        for row in records:
            self.with_delay().create_invoice_line(row)

    @job(default_channel='root')
    @api.model
    def create_invoice_line(self, row: dict):
        """Create an invoice line from a GDS report row."""
        vals = {
            'fees': json.dumps(self._get_gds_fees(row)),
            'invoice_date': self._get_gds_date(row),
            'invoice_type': 'gds',
            'ticket_number': row.get('Ticket number'),
            'locator': row.get('Record locator'),
            'office_id': row.get('Office ID'),
            'passenger': row.get("Passenger's name"),
            'vendor_id': row.get('Airline Code')
        }
        return self.env['ofh.supplier.invoice.line'].create(vals)

    @api.model
    def _get_gds_fees(self, row: dict) -> dict:
        """Put GDS fees in a dictionary to be saved in the invoice model
        Arguments:
            row {dict} -- dict contain GDS report row data
        Returns:
            dict -- dict contain invoice line fees break down.
        """
        fees = {
            'Base fare': row.get('Base fare', 0.0),
            'Tax': row.get('Tax', 0.0),
            'Net': row.get('Net', 0.0),
            'Fee': row.get('Fee', 0.0),
            'IATA commission': row.get('IATA commission', 0.0),
        }
        return fees

    @api.model
    def _get_gds_date(self, row: dict) -> str:
        """Helper method to convert date to Odoo format
        Arguments:
           row {dict} -- dict contain GDS report row data.
        Returns:
            str -- string represent the date on the odoo format.
        """

        dt = datetime.strptime(row.get('Date'), '%d/%m/%y')
        return fields.Date.to_string(dt)
