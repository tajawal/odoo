# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.addons.ofh_hub_connector.components.backend_adapter import HubAPI
from odoo.addons.queue_job.job import job
from odoo.tools.float_utils import float_is_zero


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    invoice_type = fields.Selection(
        selection_add=[('gds', 'GDS')],
    )
    invoice_status = fields.Selection(
        selection_add=[('AMND', 'Amendment')],
    )

    @api.multi
    def _gds_compute_name(self):
        self.ensure_one()
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

    @api.model
    def cron_download_gds_report(self):
        offices = self.env['ofh.gds.office'].search([])
        report_day = (datetime.now() - timedelta(days=1)).\
            strftime("%d%b").upper()
        for office in offices:
            self.with_delay()._import_gds_daily_report(
                office=office, report_day=report_day)

    @job(default_channel='root.hub')
    @api.model
    def _import_gds_daily_report(self, office, report_day):
        if not office or not report_day:
            return False
        source_model = 'import.source.command_cryptic'
        source = self.env[source_model].search(
            [('office_id', '=', office.name), ('report_day', '=', report_day)],
            limit=1)
        if not source:
            source = self.env[source_model].create({
                'office_id': office.name, 'report_day': report_day})

        backend = self.env.ref('ofh_supplier_invoice_gds.gds_import_backend')
        import_type = self.env.ref('ofh_supplier_invoice_gds.gds_import_type')

        recordset = self.env['import.recordset'].create({
            'backend_id': backend.id,
            'import_type_id': import_type.id,
            'source_id': source.id,
            'source_model': source_model,
        })

        return recordset.run_import()

    @api.multi
    def action_gds_record_locator(self):
        for line in self.filtered(lambda l: l.invoice_type == 'gds'):
            line.with_delay().gds_retrieve_pnr()

    @api.multi
    @job(default_channel='root.import')
    def gds_retrieve_pnr(self):
        self.ensure_one()
        backend = self.env['hub.backend'].search([], limit=1)
        if not backend:
            return {}

        hub_api = HubAPI(oms_finance_api_url=backend.oms_finance_api_url)

        self.order_reference = hub_api.gds_retrieve_pnr(
            office_id=self.office_id, locator=self.locator)

    @api.model
    def create(self, vals):
        record = super(OfhSupplierInvoiceLine, self).create(vals)
        if record.invoice_type == 'gds':
            if float_is_zero(
                    record.total,
                    precision_rounding=record.currency_id.rounding) or \
                    not record.locator:
                record.active = False
        return record
