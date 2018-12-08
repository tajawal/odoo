# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class OfhPaymentRequest(models.Model):

    _inherit = 'ofh.payment.request'

    supplier_invoice_ids = fields.One2many(
        string="Supplier costs",
        comodel_name='ofh.supplier.invoice.line',
        inverse_name='payment_request_id',
    )
    supplier_total_amount = fields.Monetary(
        string="Supplier Total Amount",
        currency_field='supplier_currency_id',
        compute='_compute_supplier_total_amount',
        readonly=True,
    )
    supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        comodel_name='res.currency',
        compute='_compute_supplier_total_amount',
        readonly=True,
    )

    # SAP related statuses
    reconciliation_status = fields.Selection(
        string="Supplier Status",
        selection=[
            ('pending', 'pending'),
            ('matched', 'Matched'),
            ('investigate', 'Investigate')],
        default='pending',
        required=True,
        index=True,
        readonly=True,
        inverse='_inverse_reconciliation_status',
        track_visibility='always',
    )

    @api.multi
    def _inverse_reconciliation_status(self):
        match_activity = self.env.ref(
            'ofh_payment_request.ofh_payment_request_activity_match')
        investigate_activity = self.env.ref(
            'ofh_payment_request.ofh_payment_request_activity_to_investigate')
        for rec in self:
            if rec.reconciliation_status == 'matched':
                activities = rec.activity_ids.filtered(
                    lambda a: a.activity_type_id in
                    (match_activity, investigate_activity))
                activities.action_done()
            elif rec.reconciliation_status == 'investigate':
                activities = rec.activity_ids.filtered(
                    lambda a: a.activity_type_id == match_activity)
                activities.action_done()
                rec._add_investigate_activity()

    @api.multi
    def _add_investigate_activity(self):
        self.ensure_one()
        if self.reconciliation_status != 'investigate':
            return False
        activity_type_id = self.env.ref(
            'ofh_payment_request.ofh_payment_request_activity_match').id
        deadline = fields.Date.from_string(
            fields.Date.today()) + relativedelta(days=2)
        users = self.env.ref(
            'ofh_payment_request.ofh_payment_request_manager').users
        self.env['mail.activity'].create({
            'activity_type_id': activity_type_id,
            'note': _("The payment request didn't match with any Supplier "
                      "Inovice. Please investigate it."),
            'res_id': self.id,
            'date_deadline': fields.Date.to_string(deadline),
            'res_model_id': self.env.ref(
                'ofh_payment_request.model_ofh_payment_request').id,
            'user_ids': [(6, 0, users.ids)]
        })
        return True

    @api.model
    def _get_unreconciled_payment_requests(self):
        """
        Return Unreconcilided payment request
        """
        return self.search(
            [('reconciliation_status', 'in', ['pending', 'investigate']),
             ('payment_request_status', '=', 'ready')])

    @api.multi
    @api.depends('supplier_invoice_ids', 'total_amount',
                 'request_type', 'order_type', 'order_amount',
                 'order_supplier_cost', 'order_supplier_currency')
    def _compute_supplier_total_amount(self):
        for rec in self:
            rec.supplier_total_amount = 0.0
            rec.supplier_currency_id = False
            # TODO: What about packages for now they're assuming like flights
            if rec.order_type != 'hotel':
                if rec.supplier_invoice_ids:
                    rec.supplier_total_amount = sum(
                        [inv.total for inv in rec.supplier_invoice_ids])
                    rec.supplier_currency_id = \
                        rec.supplier_invoice_ids.mapped('currency_id')[0]
                continue
            if rec.request_type == 'refund':
                rec.supplier_total_amount = \
                    ((rec.total_amount / rec.order_amount) *
                     rec.order_supplier_cost)
            else:
                # Case of amendment
                rec.supplier_total_amount = rec.total_amount
            rec.supplier_currency_id = rec.order_supplier_currency
