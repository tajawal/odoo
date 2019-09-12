# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).	

from odoo import fields, models, _


class OfhPaymentGatewayLine(models.Model):
    _inherit = 'ofh.payment.gateway.line'
