# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime
from odoo import api, fields, models
from odoo.addons.queue_job.job import job
from odoo.tools import float_is_zero


try:
    from odoo.addons.server_environment import serv_config
except ImportError:
    logging.getLogger('odoo.module').warning(
        'server_environment not available in addons path. '
        'server_env_connector_magento will not be usable')

_logger = logging.getLogger(__name__)

SAP_XML_URL = 'sap_xml_api_url'
SAP_XML_USERNAME = 'sap_xml_api_username'
SAP_XML_PASSWORD = 'sap_xml_api_password'
SOURCE = 'hub_source'


class OfhPaymentRequest(models.Model):

    _inherit = 'ofh.payment.request'

    sap_status = fields.Selection(
        string='SAP status',
        selection=[
            ('pending', 'Pending'),
            ('not_in_sap', "Not In SAP"),
            ('in_sap', "Sale & Payment In SAP"),
            ('payment_in_sap', "Payment in SAP"),
            ('sale_in_sap', 'Sale in SAP')],
        default='pending',
        required=True,
        index=True,
        readonly=True,
        track_visibility='always',
    )
    integration_status = fields.Selection(
        string="Integration Status",
        selection=[
            ('not_sent', 'Not sent'),
            ('payment_sent', 'Payment sent'),
            ('sale_sent', 'Sale sent'),
            ('sale_payment_sent', 'Sale & Payment sent')],
        readonly=True,
        required=True,
        default='not_sent',
        index=True,
        track_visibility='always',
    )
    sap_xml_sale_ref = fields.Char(
        string="SAP XML Order #",
        readonly=True,
        track_visibility='always',
    )
    sap_xml_file_ref = fields.Char(
        string="SAP XML File ID",
        readonly=True,
        track_visibility='always',
    )
    # SAP Conditions:
    sap_zsel = fields.Monetary(
        string="SAP ZSEL",
        currency_field='currency_id',
        compute='_compute_sap_zsel',
        readonly=True,
        store=False,
    )
    sap_payment_amount1 = fields.Monetary(
        string="SAP Payment Amount1",
        currency_field='currency_id',
        compute='_compute_sap_zsel',
        readonly=True,
        store=False,
    )
    sap_payment_amount2 = fields.Monetary(
        string="SAP Payment Amount2",
        currency_field='currency_id',
        compute='_compute_sap_zsel',
        readonly=True,
        store=False,
    )
    sap_zvd1 = fields.Monetary(
        string="SAP ZVD1",
        currency_field='supplier_currency_id',
        compute='_compute_sap_zvd1',
        readonly=True,
        store=False,
    )
    manual_sap_zvd1 = fields.Monetary(
        string="Manual SAP ZVD1",
        currency_field='manual_sap_zvd1_currency',
        track_visibility='onchange',
    )
    manual_sap_zvd1_currency = fields.Many2one(
        string="Manual SAP ZVD1 Currency",
        comodel_name='res.currency',
        track_visibility='onchange',
    )
    sap_zdis = fields.Monetary(
        string="SAP ZDIS",
        currency_field='currency_id',
        compute='_compute_sap_zsel',
        readonly=True,
        store=False,
    )
    sap_zvt1 = fields.Monetary(
        string="SAP ZVT1",
        currency_field='currency_id',
        compute='_compute_sap_zvt1',
        readonly=True,
        store=False,
    )
    sap_pnr = fields.Char(
        string="SAP PNR",
        compute='_compute_sap_pnr',
        readonly=True,
        store=False,
    )
    sap_line_ids = fields.One2many(
        string="SAP Sale Lines",
        comodel_name='ofh.payment.request.sap.line',
        inverse_name='payment_request_id',
        compute="_compute_sap_line_ids",
        readonly=True,
        store=False,
    )

    sap_change_fee_zsel = fields.Monetary(
        string="SAP Change Fee ZSEL",
        currency_field='currency_id',
        compute='_compute_change_fee_line',
        readonly=True,
        store=False,
    )

    sap_change_fee_zvt1 = fields.Monetary(
        string="SAP Change Fee ZVT1",
        currency_field='currency_id',
        compute='_compute_change_fee_line',
        readonly=True,
        store=False,
    )

    sap_change_fee_service_item = fields.Char(
        string="SAP SERVICE ITEM",
        compute='_compute_change_fee_line',
        readonly=True,
        store=False,
    )

    sap_change_fee_tax_code = fields.Char(
        string="Change Fee Tax Code",
        compute='_compute_change_fee_line',
        readonly=True,
        store=False,
    )

    sap_tax_code = fields.Char(
        string="SAP Tax Code",
        compute='_compute_sap_zvt1',
        readonly=True,
        store=False,
    )

    @api.multi
    @api.depends('order_discount', 'request_type', 'total_amount', 'discount',
                 'order_amount', 'sap_zvd1', 'is_egypt')
    def _compute_sap_zsel(self):
        """Compute Gross revenue, discount, payment amount 1 and 2."""
        for rec in self:
            rec.sap_zsel = rec.sap_zdis = rec.sap_payment_amount1 = \
                rec.sap_payment_amount2 = 0.0
            if rec.matching_status not in ('matched', 'not_applicable'):
                continue
            if rec.payment_request_status == 'incomplete':
                continue
            if rec.request_type == 'void':
                continue
            # For the amendment we take whatever amounts are in the PR
            if rec.request_type == 'charge':
                # Subtracted changeFee in case of
                # Charges i.e (- rec.change_fee)
                rec.sap_zsel = rec.total_amount - rec.change_fee
                rec.sap_zdis = rec.discount
                rec.sap_payment_amount1 = rec.total_amount * -1
                rec.sap_payment_amount2 = rec.total_amount
            # For refunds we prorate the discount using the initial order
            # amount and initial order discount.
            else:
                if rec.order_amount:
                    discount = \
                        (rec.total_amount / rec.order_amount) * \
                        rec.order_discount
                else:
                    discount = 0
                discount = abs(discount)
                # Added changeFee in case of Refunds i.e (+ rec.change_fee)
                rec.sap_zsel = rec.total_amount + discount + rec.change_fee
                rec.sap_zdis = discount
                rec.sap_payment_amount1 = rec.total_amount
                rec.sap_payment_amount2 = rec.total_amount * -1

            # For Egypt orders the zsel is the zvd1 amount
            if rec.is_egypt:
                rec.sap_zsel = rec.sap_zvd1

    @api.multi
    @api.depends(
        'supplier_total_amount', 'supplier_shamel_total_amount',
        'supplier_currency_id', 'fare_difference', 'penalty',
        'matching_status', 'order_type', 'is_full_refund',
        'estimated_cost_in_supplier_currency', 'order_id.line_ids')
    def _compute_sap_zvd1(self):
        """ Compute supplier cost to send to SAP."""
        for rec in self:
            rec.sap_zvd1 = 0.0
            # Check if manual_sap_zvd1 zvd1 is set assign it to sap_zvd1
            if not float_is_zero(
                    rec.manual_sap_zvd1,
                    precision_rounding=rec.currency_id.rounding):
                rec.sap_zvd1 = abs(rec.manual_sap_zvd1)
                continue
            if rec.matching_status == 'unmatched':
                continue
            # if no supplier for flight payment request continue
            if rec.matching_status == 'not_applicable' and \
               rec.order_type == 'flight':
                continue
            if rec.payment_request_status == 'incomplete':
                continue
            if rec.request_type == 'void':
                continue
            if not float_is_zero(
                    rec.supplier_shamel_total_amount,
                    precision_rounding=rec.supplier_currency_id.rounding):
                rec.sap_zvd1 = rec.supplier_shamel_total_amount
            else:
                rec.sap_zvd1 = rec.supplier_total_amount
            rec.sap_zvd1 = abs(rec.sap_zvd1)

            # https://trello.com/c/CQvak1xI/125-fix-order-supplier-cost
            # we using the payment request currency, bc most probably the
            # zvd1 is zero because there are not order supplier cost nor
            # order supplier currency
            if float_is_zero(
                    rec.sap_zvd1, precision_rounding=rec.currency_id.rounding)\
                    and rec.order_type == 'hotel':
                if rec.is_full_refund:
                    rec.sap_zvd1 = abs(sum([
                        l.supplier_cost_amount
                        for l in rec.order_id.line_ids]))
                else:
                    rec.sap_zvd1 = abs(rec.estimated_cost_in_supplier_currency)

    @api.multi
    @api.depends('output_vat_amount')
    def _compute_sap_zvt1(self):
        """ Compute output VAT to SAP."""
        for rec in self:
            rec.sap_zvt1 = 0.0
            if rec.matching_status not in ('matched', 'not_applicable'):
                continue
            if rec.payment_request_status == 'incomplete':
                continue
            if rec.request_type == 'void':
                continue

            # If Charge subtract ChangeFeeVat
            if rec.request_type == 'charge':
                rec.sap_zvt1 = \
                    rec.output_vat_amount - rec.change_fee_vat_amount
            # If Refund Add ChangeFeeVat
            if rec.request_type == 'refund':
                rec.sap_zvt1 = \
                    rec.output_vat_amount + rec.change_fee_vat_amount

            # Tax Code logic is redefined
            if rec.sap_zvt1 == 0.0:
                rec.sap_tax_code = "SZ"
            else:
                rec.sap_tax_code = "SS"

    @api.multi
    @api.depends('supplier_invoice_ids.locator')
    def _compute_sap_pnr(self):
        for rec in self:
            if not rec.supplier_invoice_ids:
                rec.sap_pnr = ''
                continue
            rec.sap_pnr = ','.join(
                set(rec.supplier_invoice_ids.mapped('locator')))

    @api.multi
    @api.depends('supplier_invoice_ids')
    def _compute_sap_line_ids(self):
        for rec in self:
            sap_line_model = self.env['ofh.payment.request.sap.line']
            if rec.sap_line_ids or not rec.supplier_invoice_ids:
                continue
            if rec.supplier_invoice_ids.filtered(
                    lambda l: l.invoice_type != 'gds' or
                    float_is_zero(
                        l.total, precision_digits=l.currency_id.rounding)):
                continue
            for line in rec.supplier_invoice_ids:
                rec.sap_line_ids |= sap_line_model.create({
                    'payment_request_id': rec.id,
                    'supplier_invoice_line': line.id
                })

    @api.multi
    def action_send_multiple_payment_requests_to_sap(self):
        """Send multiple payment requests to SAP."""
        for rec in self:
            rec.with_delay().send_payment_request_to_sap()

    @job(default_channel='root.sap')
    @api.multi
    def send_payment_request_to_sap(self):
        """Send payment request to SAP through SAP-XML-API."""
        # All void payment request should be handleded by automation.
        self.ensure_one()
        _logger.info(
            f"Check condition to send PR# {self.track_id} to SAP.")
        if self.request_type == 'void':
            _logger.warn(f"PR# {self.track_id} is `void`. Skipp it.")
            return False

        # Case where nothing should be done everything is in SAP.
        if self.sap_status == 'in_sap':
            _logger.warn(f"PR# {self.track_id} already in SAP. Skipp it.")
            return False

        if self.matching_status not in ('matched', 'not_applicable'):
            _logger.warn(f"PR# {self.track_id} is not matched yet. Skipp it.")
            return False

        if self.payment_request_status == 'incomplete':
            _logger.warn(f"PR# {self.track_id} is incomplete. Skipp it.")
            return False

    @api.multi
    @api.depends('change_fee', 'change_fee_vat_amount', 'order_type')
    def _compute_change_fee_line(self):
        """Compute Gross revenue, discount, payment amount 1 and 2."""
        for rec in self:
            rec.sap_change_fee_zsel = rec.sap_change_fee_zvt1 = 0.0

            # Change Fee Line Item ZSEL and ZVT1
            rec.sap_change_fee_zsel = rec.change_fee
            rec.sap_change_fee_zvt1 = rec.change_fee_vat_amount
            # TODO: move it to SAP-XML-API we should not keep any master data
            # in finance hub. Also we need to remove it as field.
            if rec.order_type == 'flight':
                rec.sap_change_fee_service_item = '700000548'
            else:
                rec.sap_change_fee_service_item = '700000549'
            rec.sap_change_fee_tax_code = "SZ" if \
                rec.sap_change_fee_zvt1 == 0.0 else "SS"
