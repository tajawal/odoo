# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
