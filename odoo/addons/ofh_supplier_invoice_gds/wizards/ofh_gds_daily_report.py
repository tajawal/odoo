# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class OfhGdsDailyReport(models.TransientModel):

    _name = 'ofh.gds.daily.report'

    date_from = fields.Date(
        string="Date From",
        required=True,
        default=fields.Date.context_today,
    )
    date_to = fields.Date(
        string="Date to",
        required=True,
        default=fields.Date.context_today,
    )

    @api.multi
    @api.constrains('date_from', 'date_to')
    def _check_report_dates(self):
        for rec in self:
            if fields.Date.from_string(rec.date_to) < fields.Date.from_string(
                    rec.date_from):
                raise ValidationError(
                    _("Date to must be bigger than Date from."))

    @api.multi
    def download_gds_report(self):
        self.ensure_one()
        current_date = fields.Date.from_string(self.date_from)
        offices = self.env['ofh.gds.office'].search([])
        invoice_model = self.env['ofh.supplier.invoice.line']
        while current_date <= fields.Date.from_string(self.date_to):
            print(fields.Date.to_string(current_date))
            current_date = current_date + timedelta(days=1)
            for office in offices:
                invoice_model.with_delay()._import_gds_daily_report(
                    office=office,
                    report_day=current_date.strftime("%d%b").upper())
