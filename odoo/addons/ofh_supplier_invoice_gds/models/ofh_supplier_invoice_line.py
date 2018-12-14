# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    invoice_type = fields.Selection(
        selection_add=[('gds', 'GDS')],
    )
    gds_base_fare_amount = fields.Monetary(
        string="Base Fare",
        compute='_compute_fees',
        currency_field='currency_id',
        readonly=True,
    )
    gds_tax_amount = fields.Monetary(
        string="Tax",
        compute='_compute_fees',
        currency_field='currency_id',
        readonly=True,
    )
    gds_net_amount = fields.Monetary(
        string="Net",
        compute='_compute_fees',
        currency_field='currency_id',
        readonly=True,
    )
    gds_fee_amount = fields.Monetary(
        string="Fee",
        compute='_compute_fees',
        currency_field='currency_id',
        readonly=True,
    )
    gds_iata_commission_amount = fields.Monetary(
        string="IATA Commission",
        compute='_compute_fees',
        currency_field='currency_id',
        readonly=True,
    )
    gds_alshamel_cost = fields.Monetary(
        string='Alshamel Cost',
        currency_field='currency_id',
        compute='_compute_gds_alshamel_cost',
    )
    invoice_status = fields.Selection(
        selection_add=[('AMND', 'Amendment')],
    )

    @api.multi
    def _gds_compute_name(self):
        self.ensure_one
        self.name = '{}_{}{}'.format(
            self.invoice_type, self.ticket_number, self.invoice_status)

    @api.multi
    @api.depends('currency_id', 'total')
    def _compute_gds_alshamel_cost(self):
        """Shamel cost is 1% of the invoice line total price."""
        currency = self.env.ref('base.KWD')
        for rec in self:
            if rec.currency_id != currency:
                continue
            rec.gds_alshamel_cost = rec.total * 0.01

    @api.multi
    def _gds_compute_fees(self, fees: dict) -> None:
        self.ensure_one()
        if not fees:
            self.gds_base_fare_amount = self.gds_tax_amount = \
                self.gds_net_amount = \
                self.gds_fee_amount = self.gds_iata_commission_amount = 0.0
        else:
            self.gds_base_fare_amount = fees.get('BaseFare', 0.0)
            self.gds_tax_amount = fees.get('Tax', 0.0)
            self.gds_net_amount = fees.get('Net', 0.0)
            self.gds_fee_amount = fees.get('FEE', 0.0)
            self.gds_iata_commission_amount = fees.get('IATA COMM', 0.0)
