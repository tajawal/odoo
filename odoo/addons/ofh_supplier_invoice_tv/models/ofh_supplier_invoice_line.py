# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.addons.queue_job.job import job
from datetime import datetime, timedelta

class OfhSupplierInvoiceLine(models.Model):
    _inherit = 'ofh.supplier.invoice.line'

    invoice_type = fields.Selection(
        selection_add=[('tv', 'Travelutionary')],
    )
    supplier_reference = fields.Char(
        string="Supplier Reference",
        readonly=True,
    )
    booked_by_branch = fields.Char(
        string="Booked By Branch",
        readonly=True,
    )
    booked_by_user = fields.Char(
        string="Booked By User",
        readonly=True,
    )

    @api.multi
    def _tv_compute_name(self):
        self.ensure_one()
        self.name = '{}_{}_{}'.format(
            self.invoice_type, self.locator, self.ticket_number)

    @api.model
    def cron_download_tv_report(self):
        date_from = (datetime.now() - timedelta(days=1)). \
            strftime("%Y-%m-%d %H:%M:%S")
        date_to = (datetime.now()). \
            strftime("%Y-%m-%d %H:%M:%S").upper()

        self.with_delay()._import_tv_daily_report(
            date_from=date_from, date_to=date_to)

    @job(default_channel='root.hub')
    @api.model
    def _import_tv_daily_report(self, date_from, date_to):
        if not date_from or not date_to:
            return False
        source_model = 'import.source.tv_report'
        source = self.env[source_model].search(
            [('date_from', '=', date_from), ('date_to', '=', date_to)],
            limit=1)
        if not source:
            source = self.env[source_model].create({
                'date_from': date_from, 'date_to': date_to})

        backend = self.env.ref('ofh_supplier_invoice_tv.tv_import_backend')
        import_type = self.env.ref('ofh_supplier_invoice_tv.tv_import_type')

        recordset = self.env['import.recordset'].create({
            'backend_id': backend.id,
            'import_type_id': import_type.id,
            'source_id': source.id,
            'source_model': source_model,
        })

        return recordset.run_import()
