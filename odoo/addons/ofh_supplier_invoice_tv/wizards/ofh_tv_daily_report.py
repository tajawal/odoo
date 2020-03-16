# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class OfhTvDailyReport(models.TransientModel):
    _name = 'ofh.tv.daily.report'

    date_from = fields.Datetime(
        string="Date From",
        required=True,
        default=fields.Date.context_today,
    )
    date_to = fields.Datetime(
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
    def download_tv_report(self):
        self.ensure_one()
        invoice_model = self.env['ofh.supplier.invoice.line']
        invoice_model.with_delay()._import_tv_daily_report(
            date_from=self.date_from,
            date_to=self.date_to)
