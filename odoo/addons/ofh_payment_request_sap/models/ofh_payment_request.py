# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime
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

CREDIT_CARD_PAYMENT_PROVIDERS = [
    'checkoutcom',
    'fort',
    'payfort',
    'sadad',
    'hyperpay',
    'tp',
]


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
                 'order_amount', 'sap_zvd1', 'is_egypt')
    def _compute_sap_zsel(self):
        """Compute Gross revenue, discount, payment amount 1 and 2."""
        for rec in self:
            rec.sap_zsel = rec.sap_zdis = rec.sap_payment_amount1 = \
                rec.sap_payment_amount2 = 0.0
            if rec.reconciliation_status not in ('matched', 'not_applicable'):
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
        'supplier_currency_id', 'fare_difference', 'penalty')
    def _compute_sap_zvd1(self):
        """ Compute supplier cost to send to SAP."""
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
            rec.sap_zvd1 = abs(rec.sap_zvd1)

            # https://trello.com/c/CQvak1xI/125-fix-order-supplier-cost
            # we using the payment request currency, bc most probably the
            # zvd1 is zero because there are not order supplier cost nor
            # order supplier currency
            if float_is_zero(
                    rec.sap_zvd1, precision_rounding=rec.currency_id.rounding)\
                    and rec.order_type == 'hotel':
                rec.sap_zvd1 = abs(rec.fare_difference - rec.penalty)

    @api.multi
    @api.depends('output_vat_amount')
    def _compute_sap_zvt1(self):
        """ Compute output VAT to SAP."""
        for rec in self:
            rec.sap_zvt1 = 0.0
            if rec.reconciliation_status not in ('matched', 'not_applicable'):
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

    @api.model
    def _get_payment_request_not_sent_by_integration(self):
        return self.search(
            [('integration_status', '!=', 'sale_payment_sent'),
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

    @job(default_channel='root')
    @api.model
    def get_sap_xml_details(self):
        """Update payment request with integration details.
        Use the SAP-XML-API API to get the integration details.
        """
        pr_not_in_integration = \
            self._get_payment_request_not_sent_by_integration()
        pr_not_in_integration = pr_not_in_integration.with_context(
            tracking_disable=True)
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
        _logger.info(
            f"Updating Payment Request {self.track_id} Integration status")
        refund_order = refund_doc = {}
        if self.integration_status in ('not_sent', 'payment_sent'):
            _logger.info(f"Check if sale part has been sent.")
            refund_order = sap_xml.get_refund_order_details({
                'orderNumber': self.order_reference,
                'trackId': self.track_id,
                'source': source,
                'requestType': 'refund_order' if
                self.request_type == 'refund' else 'sale_order'})
        if self.integration_status in ('not_sent', 'sale_sent'):
            _logger.info(f"Check if payment part has been sent.")
            refund_doc = sap_xml.get_refund_doc_details({
                'orderNumber': self.order_reference,
                'trackId': self.track_id,
                'source': source,
                'requestType': 'refund_doc' if
                self.request_type == 'refund' else 'sale_doc'})

        if refund_order and refund_doc:
            integration_status = self._get_new_integration_status(
                'sale_payment_sent')
            return self.write({
                'integration_status': integration_status,
                'sap_xml_sale_ref': refund_order.get('BookingNumber'),
                'sap_xml_file_ref': refund_order.get('FileID')})
        elif refund_order:
            integration_status = self._get_new_integration_status('sale_sent')
            return self.write({
                'integration_status': integration_status,
                'sap_xml_sale_ref': refund_order.get('BookingNumber'),
                'sap_xml_file_ref': refund_order.get('FileID')})
        elif refund_doc:
            integration_status = self._get_new_integration_status(
                'payment_sent')
            return self.write({
                'integration_status': integration_status,
                'sap_xml_sale_ref': refund_doc.get('HeaderText'),
                'sap_xml_file_ref': refund_doc.get('Assignment')})
        return False

    @api.multi
    def action_send_multiple_payment_requests_to_sap(self):
        """Send multiple payment requests to SAP."""
        for rec in self:
            rec.with_delay().send_payment_request_to_sap()

    @job(default_channel='root')
    @api.multi
    def send_payment_request_to_sap(self):
        """Send payment request to SAP through SAP-XML-API."""
        # All void payment request should be handleded by automation.
        _logger.info(
            f"Check condition to send PR# {self.track_id} to SAP.")
        if self.request_type == 'void':
            _logger.warn(f"PR# {self.track_id} is `void`. Skipp it.")
            return False

        # Case where nothing should be done everything is in SAP.
        if self.sap_status == 'in_sap':
            _logger.warn(f"PR# {self.track_id} already in SAP. Skipp it.")
            return False

        if self.reconciliation_status not in ('matched', 'not_applicable'):
            _logger.warn(f"PR# {self.track_id} is not matched yet. Skipp it.")
            return False

        if self.payment_request_status == 'incomplete':
            _logger.warn(f"PR# {self.track_id} is incomplete. Skipp it.")
            return False

        integration_details = self._get_server_env()
        sap_xml = SapXmlApi(
            sap_xml_url=integration_details.get(SAP_XML_URL),
            sap_xml_username=integration_details.get(SAP_XML_USERNAME),
            sap_xml_password=integration_details.get(SAP_XML_PASSWORD))

        source = integration_details.get(SOURCE)
        _logger.info(f"Start sending PR# {self.track_id} to SAP.")
        # Case where both sale and payment should be sent to SAP.
        if self.sap_status in ('pending', 'not_in_sap', 'payment_in_sap'):
            try:
                payload = self._get_sale_sap_xml_api_payload(source)
                _logger.info(
                    f"Sending sale part to SAP with the "
                    f"following values: {payload}")
                sap_xml.sent_payment_request(payload)
            except Exception:
                _logger.warn("Sending sale part to SAP failed.")
                self.message_post("Sending sale part to SAP failed.")

        if self.sap_status in ('pending', 'not_in_sap', 'sale_in_sap'):
            try:
                payload = self._get_payment_sap_xml_api_payload(source)
                _logger.info(
                    f"Sending payment part to SAP with the "
                    f"following values: {payload}")
                sap_xml.sent_payment_request(payload)
            except Exception:
                _logger.warn("Sending payment part to SAP failed.")
                self.message_post("Sending payment part to SAP failed.")

        _logger.info(
            "Sending is done. Updating Integartion status "
            "after sending is done.")
        self.update_sap_xml_details()

    @api.multi
    def _get_new_integration_status(self, integration_status: str) -> str:
        """Return the new integration status depending on the previous status
        Arguments:
            integration_status {str} -- the new integration status
        Returns:
            str -- the new status that should be used.
        """
        self.ensure_one()
        old_integration_status = self.integration_status
        if old_integration_status == 'sale_payment_sent':
            return old_integration_status
        if (old_integration_status == 'payment_sent' and
           integration_status == 'sale_sent') or \
           (old_integration_status == 'sale_sent' and
           integration_status == 'payment_sent'):
            return 'sale_payment_sent'
        return integration_status

    @api.multi
    def _get_sale_sap_xml_api_payload(self, source):
        """Return the sale payload to send to SAP-XML-API."""
        self.ensure_one()
        booking_date = datetime.strftime(
            fields.Datetime.from_string(
                self.updated_at), '%Y%m%d')
        payload = {
            'orderId': self.order_id,
            'trackId': self.track_id,
            'source': source,
            'requestType': 'refund_order' if
            self.request_type == 'refund' else 'sale_order',
            'updates': {
                'header': {
                    'BookingDate': booking_date,
                }
            }
        }

        if self.sap_line_ids:
            payload['updates']['lineItems'] = [
                line.to_dict() for line in self.sap_line_ids]
        else:
            payload['updates']['lineItems'] = [{
                'item_general': {
                    'VATTaxCode': self.sap_tax_code,
                    'pnr': self.sap_pnr,
                    'BillingDate': booking_date,
                },
                'item_condition': {
                    'ZVD1': self.sap_zvd1,
                    # https://trello.com/c/CQvak1xI/125-fix-order-supplier-cost
                    'ZVD1_CURRENCY': self.supplier_currency_id.name if
                    self.supplier_currency_id else self.currency_id.name,
                    'ZSEL': self.sap_zsel,
                    'ZSEL_CURRENCY': self.currency_id.name,
                    'ZVT1': self.sap_zvt1,
                    'ZVT1_CURRENCY': self.currency_id.name,
                    'ZDIS': self.sap_zdis,
                    'ZDIS_CURRENCY': self.currency_id.name,
                }
            }]

        if not float_is_zero(
                self.change_fee,
                precision_rounding=self.currency_id.rounding):
            change_fee_line_item = self.get_change_fee_line_item()
            payload['updates']['lineItems'].append(change_fee_line_item)

        return payload

    @api.multi
    def get_change_fee_line_item(self):
        """Return the Change Fee LineItem."""
        self.ensure_one()
        booking_date = datetime.strftime(
            fields.Datetime.from_string(
                self.updated_at), '%Y%m%d')

        line_item = {
            'item_general': {
                'VATTaxCode': self.sap_change_fee_tax_code,
                'ServiceItem': self.sap_change_fee_service_item,
                'BillingDate': booking_date,
                'GDSCode': "",
            },
            'item_condition': {
                'ZVD1': 0.0,
                'ZVD1_CURRENCY': self.supplier_currency_id.name if
                self.supplier_currency_id else self.currency_id.name,
                'ZSEL': self.sap_change_fee_zsel,
                'ZSEL_CURRENCY': self.currency_id.name,
                'ZVT1': self.sap_change_fee_zvt1,
                'ZVT1_CURRENCY': self.currency_id.name,
                'ZDIS': 0.0,
                'ZDIS_CURRENCY': self.currency_id.name,
            }
        }

        return line_item

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

    @api.multi
    def _get_payment_sap_xml_api_payload(self, source):
        """Return the payment payload to send to SAP-XML-API."""
        self.ensure_one()
        payload = {
            'orderId': self.order_id,
            'trackId': self.track_id,
            'source': source,
            'requestType': 'refund_doc' if
            self.request_type == 'refund' else 'sale_doc',
            'updates': {
                'DocumentDate': datetime.strftime(
                    fields.Datetime.from_string(
                        self.updated_at), '%Y%m%d'),
                'Amount1': self.sap_payment_amount1,
                'Amount2': self.sap_payment_amount2,
                'Currency': self.currency_id.name,
            }
        }
        if self.auth_code:
            payload['updates']['ReferenceKey3'] = self.auth_code

        return payload

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
