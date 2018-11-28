# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class OfhPaymentRequestIntegrationUpdate(models.TransientModel):

    _name = 'ofh.payment.request.integration.update'

    @api.multi
    def update_integration_details(self):
        self.ensure_one()
        return self.env['ofh.payment.request'].get_sap_xml_details()
