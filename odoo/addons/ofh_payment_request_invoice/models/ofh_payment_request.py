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
        help="Supplier total amount without Shamel cost",
    )
    supplier_shamel_total_amount = fields.Monetary(
        string="Supplier Shamel Total Amount",
        currency_field='supplier_currency_id',
        compute='_compute_supplier_total_amount',
        readonly=True,
        help="Supplier total amount including Shamel cost",
    )
    supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        comodel_name='res.currency',
        compute='_compute_supplier_total_amount',
        readonly=True,
    )

    @api.multi
    def _add_investigate_activity(self):
        activity_type_id = self.env.ref(
            'ofh_payment_request.ofh_payment_request_activity_match').id
        users = self.env.ref(
            'ofh_payment_request.ofh_payment_request_manager').users
        deadline = fields.Date.from_string(
            fields.Date.today()) + relativedelta(days=2)
        note = _("The payment request didn't match with any Supplier "
                 "Inovice. Please investigate it.")
        model_id = self.env.ref(
            'ofh_payment_request.model_ofh_payment_request').id
        for rec in self:
            if rec.reconciliation_status != 'investigate':
                continue
            rec.env['mail.activity'].create({
                'activity_type_id': activity_type_id,
                'note': note,
                'res_id': rec.id,
                'date_deadline': fields.Date.to_string(deadline),
                'res_model_id': model_id,
                'user_ids': [(6, 0, users.ids)]
            })
        return True

    @api.model
    def _get_unreconciled_payment_requests(self):
        """
        Return Unreconcilided payment request
        """
        return self.search([
            ('reconciliation_status', 'in', ['pending', 'investigate']),
            ('payment_request_status', '=', 'ready'),
            '|',
            ('hub_supplier_reference', '!=', False),
            ('manual_supplier_reference', '!=', False)],
            order='created_at asc')

    @api.multi
    @api.depends('supplier_invoice_ids', 'total_amount',
                 'request_type', 'order_type', 'order_amount',
                 'order_supplier_cost', 'order_supplier_currency')
    def _compute_supplier_total_amount(self):
        for rec in self:
            rec.supplier_total_amount = rec.supplier_shamel_total_amount = 0.0
            rec.supplier_currency_id = False
            # TODO: What about packages for now they're assuming like flights
            if rec.order_type != 'hotel':
                if rec.supplier_invoice_ids:
                    kwd_invoices = rec.supplier_invoice_ids.filtered(
                        lambda i: i.currency_id == self.env.ref('base.KWD'))
                    rec.supplier_total_amount = sum(
                        [i.gds_net_amount if
                         i.invoice_type == 'gds' else i.total
                         for i in rec.supplier_invoice_ids])
                    rec.supplier_currency_id = \
                        rec.supplier_invoice_ids.mapped('currency_id')[0]
                    if not kwd_invoices:
                        continue
                    # Shamel cost mininum is 2 KWD. we take the absolute value
                    # because the cost will be negative in case of refund.
                    shamel_cost = max(abs(
                        sum([inv.gds_alshamel_cost for inv in kwd_invoices])),
                        2)
                    rec.supplier_shamel_total_amount = \
                        rec.supplier_total_amount + shamel_cost
                continue
            if rec.request_type == 'refund':
                rec.supplier_total_amount = \
                    ((rec.total_amount / rec.order_amount) *
                     rec.order_supplier_cost)
            else:
                # Case of amendment
                rec.supplier_total_amount = rec.total_amount
            rec.supplier_currency_id = rec.order_supplier_currency
