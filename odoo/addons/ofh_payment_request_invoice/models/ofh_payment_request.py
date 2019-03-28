# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.queue_job.job import job


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
    estimated_cost_in_supplier_currency = fields.Monetary(
        string="Estimated Cost in Supplier Currency",
        currency_field='supplier_currency_id',
        readonly=True,
        compute='_compute_estimated_cost',
        store=False,
    )
    supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        comodel_name='res.currency',
        compute='_compute_supplier_total_amount',
        readonly=True,
    )
    reconciliation_tag = fields.Selection(
        string="Deal/Loss",
        selection=[
            ('deal', 'DEAL'),
            ('loss', 'LOSS'),
            ('none', 'N/A')],
        compute='_compute_reconciliation_tag',
        readonly=True,
        store=False,
    )
    reconciliation_amount = fields.Monetary(
        string="Deal/Loss Amount",
        compute='_compute_reconciliation_tag',
        currency_field='supplier_currency_id',
        readonly=True,
        store=False,
    )

    @api.multi
    @api.depends(
        'insurance', 'fare_difference', 'penalty',
        'supplier_currency_id', 'currency_id')
    def _compute_estimated_cost(self):
        res = super(OfhPaymentRequest, self)._compute_estimated_cost()
        for rec in self:
            rec.estimated_cost_in_supplier_currency = 0.0
            if not rec.supplier_currency_id:
                continue
            rec.estimated_cost_in_supplier_currency = \
                rec.currency_id.compute(
                    rec.estimated_cost, rec.supplier_currency_id)
        return res

    @api.model
    def _get_unreconciled_payment_requests(self):
        """
        Return Unreconciled payment request
        """
        return self.search([
            ('reconciliation_status', 'in', ['pending', 'investigate']),
            ('payment_request_status', '=', 'ready'),
            '|',
            ('hub_supplier_reference', '!=', False),
            ('manual_supplier_reference', '!=', False)],
            order='created_at asc')

    @api.multi
    @api.depends('supplier_invoice_ids.gds_net_amount',
                 'supplier_invoice_ids.total', 'total_amount',
                 'request_type', 'order_type', 'order_amount', 'currency_id',
                 'order_supplier_cost', 'order_supplier_currency',
                 'reconciliation_status', 'fare_difference', 'insurance',
                 'penalty')
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
                        [i.gds_net_amount if i.invoice_type == 'gds' else
                         i.total for i in rec.supplier_invoice_ids])
                    rec.supplier_currency_id = \
                        rec.supplier_invoice_ids.mapped('currency_id')[0]
                    if not kwd_invoices:
                        continue
                    # Shamel cost minimum is 2 KWD. we take the absolute value
                    # because the cost will be negative in case of refund.
                    shamel_cost = max(abs(
                        sum([inv.gds_alshamel_cost for inv in kwd_invoices])),
                        2)
                    rec.supplier_shamel_total_amount = \
                        rec.supplier_total_amount + shamel_cost
                # If a flight don't match with any supplier invoice and is
                # marked as not applicable we reverse calculate the cost using
                # the fees of the payment request.
                elif rec.reconciliation_status == 'not_applicable':
                    if rec.request_type == 'charge':
                        rec.supplier_total_amount = \
                            rec.fare_difference + rec.insurance + rec.penalty
                    elif rec.request_type == 'refund':
                        rec.supplier_total_amount = \
                            rec.fare_difference - rec.insurance - rec.penalty
                    rec.supplier_currency_id = \
                        rec.order_supplier_currency or rec.currency_id
                continue
            if rec.request_type == 'refund':
                if rec.order_amount:
                    rec.supplier_total_amount = \
                        ((rec.total_amount / rec.order_amount) *
                         rec.order_supplier_cost)
                    rec.supplier_currency_id = rec.order_supplier_currency
            else:
                # Case of amendment
                rec.supplier_total_amount = rec.total_amount
                rec.supplier_currency_id = rec.currency_id

    @api.multi
    @api.depends(
        'supplier_invoice_ids', 'reconciliation_status', 'need_to_investigate',
        'supplier_total_amount', 'estimated_cost_in_supplier_currency',
        'request_type')
    def _compute_reconciliation_tag(self):
        for rec in self:
            rec.reconciliation_tag = 'none'
            rec.reconciliation_amount = 0
            if rec.reconciliation_status != 'matched' or \
                    rec.need_to_investigate:
                continue
            rec.reconciliation_amount = \
                abs(rec.estimated_cost_in_supplier_currency) - \
                abs(rec.supplier_total_amount)
            if rec.request_type == 'charge':
                # It's a loss because the amendment cost us more than what we
                # received from the customer.
                if rec.reconciliation_amount < 0:
                    rec.reconciliation_tag = 'loss'
                elif rec.reconciliation_amount > 0:
                    rec.reconciliation_tag = 'deal'
            else:
                # It's a deal because the refunded money to the customer
                # is less than the money received from the supplier,
                # we keep the rest to our pocket.
                if rec.reconciliation_amount < 0:
                    rec.reconciliation_tag = 'deal'
                elif rec.reconciliation_amount > 0:
                    rec.reconciliation_tag = 'loss'

    @api.multi
    def optmise_matching_result(self):
        """
        Payment requests of type charge, that matched with supplier, will
        always needs further matching investigation, as from the supplier side
        there are no difference between a ticket issued from an initial order
        or a ticket issued from an amendment. To reduce such risk we run
        a matching optimisation based on the amount.
        """
        for rec in self:
            if not rec.need_to_investigate:
                continue
            rec.with_delay()._optimise_matching()

    @api.multi
    @job(default_channel='root')
    def _optimise_matching(self):
        """ Optimise the matching logic for a given transaction using the
        the following algorithm.
        1- Apply the formula: Supplier Cost / Calculated Cost)
        2- IF the % is greater than 135, THEN remove the highest amount
            Invoice line from the Payment Request.
        3- Apply the above formula again
        4- Re-do the exercise until it is less than 135 or no more line
            items are remaining
        5- IF the % is equal to or less than 135, THEN mark as
        investigated, else change reconciliation status to `investigate`.
        """
        self.ensure_one()
        supplier_cost = self.supplier_shamel_total_amount if \
            not self.supplier_currency_id.is_zero(
                self.supplier_shamel_total_amount) else \
            self.supplier_total_amount

        invoice_lines = self.supplier_invoice_ids.sorted(
            lambda l: l.total, reverse=True)

        diff = abs(supplier_cost / self.estimated_cost_in_supplier_currency)

        while diff > 1.35:
            invoice_lines[0].payment_request_id = False
            if not self.supplier_invoice_ids:
                break
            supplier_cost = self.supplier_shamel_total_amount if \
                not self.supplier_currency_id.is_zero(
                    self.supplier_shamel_total_amount) else \
                self.supplier_total_amount
            diff = abs(
                supplier_cost / self.estimated_cost_in_supplier_currency)
            invoice_lines = self.supplier_invoice_ids.sorted(
                lambda l: l.total, reverse=True)

        if self.supplier_invoice_ids:
            self.is_investigated = True
        else:
            self.reconciliation_status = 'investigate'
        return True
