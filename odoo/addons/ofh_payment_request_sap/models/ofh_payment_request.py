# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.queue_job.job import job
from .sap_xml_api import SapXmlApi

_logger = logging.getLogger(__name__)


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
    )
    sap_xml_sale_ref = fields.Char(
        string="SAP XML Order #",
        readonly=True,
    )
    sap_xml_file_ref = fields.Char(
        string="SAP XML File ID",
        readonly=True,
    )

    @api.multi
    @api.constrains(
        'integration_status', 'sap_xml_sale_ref', 'sap_xml_file_ref')
    def _check_sap_xml_details(self):
        for rec in self:
            if rec.integration_status == 'not_sent' and \
               rec.sap_xml_sale_ref or rec.sap_xml_file_ref:
                raise ValidationError(
                    _("SAP XML details can't be filled if the payment request "
                      "has not been sent through integration."))
            if rec.integration_status != 'not_sent' and \
               not rec.sap_xml_sale_ref:
                raise ValidationError(
                    _("If the payment request is sent through integration the "
                      "'SAP XML Order' # is mandatory."))

    @api.model
    def _get_payment_request_not_sent_by_integration(self):
        return self.search([('sap_xml_sale_ref', '=', False)])

    @api.model
    def _get_sap_xml_details(self):
        """
        Update the payment requests with the integration in this occurance
        SAP-XML-API details:
            1- The order reference: ex. A80924181552_4432032R0
            2- The Order file ID: ex. 29f64621906323R0
            3- Update the reconciliation status.
        """
        pr_not_in_integration = \
            self._get_payment_request_not_sent_by_integration()
        if not pr_not_in_integration:
            return
        for payment_request in pr_not_in_integration:
            payment_request._get_integration_details()

    @job(default_channel='root')
    @api.multi
    def update_sap_xml_details(self):
        """
        Use the SAP-XML-API API to get the integration details.
        """
        self.ensure_one()
        # TODO Use config file for the db name and host
        sap_xml = SapXmlApi(
            db_name='sap_web_api_13_11',
            host='192.168.99.100',
            port=37017)
        sync_history = sap_xml.get_sync_history_by_track_id(
            self.order_reference)
        if not sync_history:
            return
        if sync_history.get('refund_order') and sync_history.get('refund_doc'):
            self.integration_status = 'sale_payment_sent'
            refund_order = sync_history.get('refund_order')
            self.sap_xml_sale_ref = refund_order.get('BookingNumber')
            self.sap_xml_file_ref = refund_order.get('FileID')
        elif sync_history.get('refund_order'):
            self.integration_status = 'sale_sent'
            refund_order = sync_history.get('refund_order')
            self.sap_xml_sale_ref = refund_order.get('BookingNumber')
            self.sap_xml_file_ref = refund_order.get('FileID')
        elif sync_history.get('refund_doc'):
            self.integration_status = 'payment_sent'
            refund_order = sync_history.get('refund_doc')
            self.sap_xml_sale_ref = refund_order.get('HeaderText')
            self.sap_xml_file_ref = refund_order.get('Assignment')

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
