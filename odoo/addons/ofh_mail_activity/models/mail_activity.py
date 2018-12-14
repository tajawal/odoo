# Copyright 2018 Tajwal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MailActivity(models.Model):

    _inherit = 'mail.activity'

    user_ids = fields.Many2many(
        string="Assigned to",
        comodel_name='res.users',
    )
    # user_id = fields.Many2one(
    #     required=False,
    #     default=False,
    # )

    @api.multi
    @api.constrains('user_id', 'user_ids')
    def _check_user_id(self):
        for rec in self:
            if rec.user_id or rec.user_ids:
                continue
            raise ValidationError(_(
                "An activity should always be assigned to someone."))

    @api.model
    def create(self, values):
        # Copy the same logic as the main stream.
        activity = super(MailActivity, self.sudo()).create(values)
        if not values.get('user_ids'):
            return activity
        self.env[activity.res_model].browse(
            activity.res_id).message_subscribe(
                partner_ids=activity.user_ids.mapped('partner_id.id'))
        if activity.date_deadline <= fields.Date.today():
            self.env['bus.bus'].sendmany([
                [(self._cr.dbname, 'res.partner', p.id),
                    {'type': 'activity_updated', 'activity_created': True}]
                for p in activity.user_ids.mapped('partner_id.id')])
        return activity

    @api.multi
    def write(self, values):
        if values.get('user_ids'):
            pre_responsibles = self.mapped('user_ids')
        res = super(MailActivity, self).write(values)
        if not values.get('user_ids'):
            return res
        for activity in self:
            partner_ids = activity.user_ids.mapped('partner_id.id')
            self.env[activity.res_model].browse(
                activity.res_id).message_subscribe(partner_ids=partner_ids)
            if activity.date_deadline <= fields.Date.today():
                self.env['bus.bus'].sendmany([
                    [(self._cr.dbname, 'res.partner', pid),
                     {'type': 'activity_updated', 'activity_created': True}]
                    for pid in partner_ids])
                old_users = pre_responsibles - activity.user_ids
                if not old_users:
                    continue
                for partner in old_users.mapped('partner_id'):
                    self.env['bus.bus'].sendone(
                        (self._cr.dbname, 'res.partner', partner.id),
                        {'type': 'activity_updated', 'activity_deleted': True})


class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    activity_user_ids = fields.Many2many(
        string='Responsible',
        comodel_name='res.users',
        related='activity_ids.user_ids',
        search='_search_activity_user_ids',
        groups="base.group_user"
    )

    @api.model
    def _search_activity_user_ids(self, operator, operand):
        return [('activity_ids.user_ids', operator, operand)]
