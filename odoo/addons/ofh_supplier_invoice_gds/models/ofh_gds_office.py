# Copyright 2019 Tajwal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OfhGDSOffice(models.Model):

    _name = 'ofh.gds.office'
    _description = 'GDS Offices'

    name = fields.Char(
        string="GDS Office ID",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    _sql_constraints = [
        ('office_id_unique', 'unique(name)', 'Office ID must be unique!'),
    ]
