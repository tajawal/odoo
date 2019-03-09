# Copyright 2019 Tajwal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, tools


class ImportSourceConsumerMixin(models.AbstractModel):

    _inherit = 'import.source.consumer.mixin'

    @api.model
    @tools.ormcache('self')
    def _selection_source_ref_id(self):
        selection = super(
            ImportSourceConsumerMixin, self)._selection_source_ref_id()
        selection.append(('import.source.command_cryptic', 'Command Cryptic'))

        return selection
