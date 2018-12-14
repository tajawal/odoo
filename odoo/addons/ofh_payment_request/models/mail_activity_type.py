# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailActivityType(models.Model):

    _inherit = 'mail.activity.type'

    category = fields.Selection(
        selection_add=[('pr', 'Payment Request')],
    )
