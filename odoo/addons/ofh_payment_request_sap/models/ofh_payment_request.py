# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.addons.queue_job.job import job
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero
from .sap_xml_api import SapXmlApi

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
            ('payment_sent', 'Payement sent'),
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

    @api.multi
    @api.constrains(
        'integration_status', 'sap_xml_sale_ref', 'sap_xml_file_ref')
    def _check_sap_xml_details(self):
        for rec in self:
            if rec.integration_status == 'not_sent' and \
               (rec.sap_xml_sale_ref or rec.sap_xml_file_ref):
                raise ValidationError(
                    _("SAP XML details can't be filled if the payment request "
                      "has not been sent through integration."))    
            if rec.integration_status != 'not_sent' and \
               not rec.sap_xml_sale_ref:
                raise ValidationError(
                    _("If the payment request is sent through integration the "
                      "'SAP XML Order #' is mandatory."))

    @api.multi
    @api.depends('order_discount', 'request_type', 'total_amount', 'discount',
                 'order_amount')
    def _compute_sap_zsel(self):
        for rec in self:
            rec.sap_zsel = rec.sap_zdis = rec.sap_payment_amount1 = \
                rec.sap_payment_amount2 = 0.0
            if rec.reconciliation_status not in ('matched', 'not_applicable'):
                continue
            if rec.payment_request_status == 'incomplete':
                continue
            if rec.request_type == 'void':
                continue
            # For the ammendment we take whatever amounts are in the PR
            if rec.request_type == 'charge':
                rec.sap_zsel = rec.total_amount
                rec.sap_zdis = rec.discount
                rec.sap_payment_amount1 = rec.total_amount * -1
                rec.sap_payment_amount2 = rec.total_amount
            # For refunds we prorate the discount using the initial order
            # amount and initial order discount.
            else:
                discount = \
                    (rec.total_amount / rec.order_amount) * rec.order_discount
                rec.sap_zsel = rec.total_amount + discount
                rec.sap_zdis = rec.discount
                rec.sap_payment_amount1 = rec.total_amount
                rec.sap_payment_amount2 = rec.total_amount * -1

    @api.multi
    @api.depends('supplier_total_amount', 'supplier_shamel_total_amount')
    def _compute_sap_zvd1(self):
        for rec in self:
            rec.sap_zvd1 = 0.0
            if rec.reconciliation_status not in ('matched', 'not_applicable'):
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

    @api.multi
    @api.depends('output_vat_amount')
    def _compute_sap_zvt1(self):
        for rec in self:
            rec.sap_zvt1 = 0.0
            if rec.reconciliation_status not in ('matched', 'not_applicable'):
                continue
            if rec.payment_request_status == 'incomplete':
                continue
            if rec.request_type == 'void':
                continue
            rec.sap_zvt1 = rec.output_vat_amount

    @api.multi
    @api.depends('supplier_invoice_ids.locator')
    def _compute_sap_pnr(self):
        for rec in self:
            if not rec.supplier_invoice_ids:
                rec.sap_pnr = ''
                continue
            rec.sap_pnr = ','.join(rec.supplier_invoice_ids.mapped('locator'))

    @api.model
    def _get_payment_request_not_sent_by_integration(self):
        return self.search([
            ('sap_xml_sale_ref', '=', False),
            ('payment_request_status', '=', 'ready')])

    @api.model
    def _get_server_env(self) -> dict:
        values = {}
        section_name = 'sap_xml_api'
        for field_name in (
                SAP_XML_URL, SAP_XML_USERNAME, SAP_XML_PASSWORD, SOURCE):
            try:
                values[field_name] = serv_config.get(section_name, field_name)
            except Exception:
                _logger.exception(
                    'error trying to read field %s in section %s',
                    field_name, section_name)
        return values

    @api.model
    def get_sap_xml_details(self):
        """Update payment request with integration details.
        Use the SAP-XML-API API to get the integration details.
        """
        pr_not_in_integration = \
            self._get_payment_request_not_sent_by_integration()
        for payment_request in pr_not_in_integration:
            payment_request.with_delay().update_sap_xml_details()

    @job(default_channel='root')
    @api.multi
    def update_sap_xml_details(self):
        """Update the payment requests with the integration details.
        SAP-XML-API details:
            1- The order reference: ex. A80924181552_4432032R0
            2- The Order file ID: ex. 29f64621906323R0
            3- Update the reconciliation status.
        """
        self.ensure_one()
        integration_details = self._get_server_env()
        sap_xml = SapXmlApi(
            sap_xml_url=integration_details.get(SAP_XML_URL),
            sap_xml_username=integration_details.get(SAP_XML_USERNAME),
            sap_xml_password=integration_details.get(SAP_XML_PASSWORD))

        source = integration_details.get(SOURCE)

        refund_order = sap_xml.get_refund_order_details({
            'orderNumber': self.order_reference,
            'trackId': self.track_id,
            'source': source,
            'requestType': 'refund_order'})
        refund_doc = sap_xml.get_refund_doc_details({
            'orderNumber': self.order_reference,
            'trackId': self.track_id,
            'source': source,
            'requestType': 'refund_doc'})

        if refund_order and refund_doc:
            return self.write({
                'integration_status': 'sale_payment_sent',
                'sap_xml_sale_ref': refund_order.get('BookingNumber'),
                'sap_xml_file_ref': refund_order.get('FileID')})
        elif refund_order:
            return self.write({
                'integration_status': 'sale_sent',
                'sap_xml_sale_ref': refund_order.get('BookingNumber'),
                'sap_xml_file_ref': refund_order.get('FileID')})
        elif refund_doc:
            self.write({
                'integration_status': 'payment_sent',
                'sap_xml_sale_ref': refund_doc.get('HeaderText'),
                'sap_xml_file_ref': refund_doc.get('Assignment')})
        return False

    @api.multi
    def write(self, vals):
        """Override the write function to make sure we update the payment
        request with the right SAP status.
        If a user upload an SAP sales report and the sap_status was already
        marked as payment sent. the new status should be
        `Sale & Payment In SAP` if the record is found in the report.
        The same thing applies when a user uploads an SAP Payment report.

        Arguments:
            vals {dict} -- Dictionary of values to be updated.

        """

        new_status = vals.get('sap_status')
        if not new_status or new_status not in \
           ('payment_in_sap', 'sale_in_sap'):
            return super(OfhPaymentRequest, self).write(vals)

        for rec in self:
            # If the last update will make both payment and sale sent to SAP
            # the SAP status should be then 'IN SAP'.
            new_vals = vals
            if rec.sap_status == 'in_sap':
                continue
            if (rec.sap_status == 'payment_in_sap' and
                    new_status == 'sale_in_sap') or \
               (rec.sap_status == 'sale_in_sap' and
                    new_status == 'payment_in_sap'):
                new_vals['sap_status'] = 'in_sap'
            super(OfhPaymentRequest, rec).write(new_vals)
        return True
