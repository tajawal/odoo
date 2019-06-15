# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if
from odoo.exceptions import MissingError
from requests.exceptions import HTTPError

RESOURCE_ERROR = 'ResourceError'
PARAMETERS_ERROR = 'ParametersError'
SYSTEM_ERROR = 'SystemError'


class OfhSaleOrderSapExporter(Component):
    _name = 'sap.sale.order.exporter'
    _inherit = 'sap.exporter'
    _apply_on = ['ofh.sale.order.sap']

    def _must_skip_order(self, sale_order) -> str:

        # If Sale order not applicable for sending
        if not sale_order.is_sale_applicable:
            return "Not Applicable for Sending"

        # If Item has already been sent successfully don't send to SAP.
        if sale_order.sap_order_ids.filtered(lambda o: o.state == 'success'):
            return "Already sent."

        # If order doesn't have line items don't send to SAP
        if not sale_order.line_ids:
            return 'Sale order has no line items.'

        # If the order has unreconciled lines don't send it to SAP.
        if sale_order.line_ids.filtered(
                lambda l: l.reconciliation_status == 'unreconciled'):
            return 'Unreconciled Lines'

        return ''

    def _must_skip_payment_request(self, payment_request) -> str:

        # If Item has already been sent successfully don't send to SAP.
        if payment_request.sap_order_ids.filtered(
                lambda o: o.state == 'success'):
            return "Already sent."

        # If the order has unreconciled lines don't send it to SAP.
        if payment_request.filtered(
                lambda p: p.reconciliation_status == 'unreconciled'):
            return 'Unreconciled Lines'

    def run(self, sap_sale_order, force=False):
        sale_order = sap_sale_order.sale_order_id
        payment_request = sap_sale_order.payment_request_id

        if not sale_order and not payment_request:
            raise MissingError("Missing binding.")
        if sale_order:
            skip_reason = self._must_skip_order(sale_order=sale_order)
        else:
            skip_reason = self._must_skip_payment_request(
                payment_request=payment_request)
        if skip_reason and not force and sap_sale_order.state != 'visualize':
            return sap_sale_order.write({
                'failing_reason': 'error',
                'failing_text': skip_reason,
                'state': 'failed',
                'sap_status': 'not_applicable',
            })

        payload = sap_sale_order._get_sale_payload()
        try:
            if sap_sale_order.state == 'visualize':
                result = self.backend_adapter.create(
                    data=payload, visualize=True)
            else:
                result = self.backend_adapter.create(data=payload)

        except HTTPError as e:
            if e.response.json().get('type', '') == RESOURCE_ERROR:
                failing_reason = 'skipped'
            else:
                failing_reason = 'error'

            return sap_sale_order.write({
                'failing_reason': failing_reason,
                'failing_text': e.response.json().get('message', ''),
                'state': 'failed',
                'sap_status': 'not_applicable',
            })

        self._after_export(sap_sale_order, response=result.json())

        return {"Success"}

    def _after_export(self, sap_sale_order, response):
        if not response:
            return

        # Update SAP Order with SAP details.
        update_values = {
            'failing_reason': 'not_applicable',
            'sap_xml': response.get('xml'),
            'sap_header_detail': json.dumps(
                response.get('data', {}).get('Header')),
        }

        if sap_sale_order.state != 'visualize':
            update_values['state'] = 'success'
        else:
            update_values['sap_status'] = 'not_applicable'

        sap_sale_order.write(update_values)

        # Update SAP lines with SAP details
        sap_lines = response.get('data', {}).get('LineItem')

        sap_line_model = self.env['ofh.sale.order.line.sap']
        for sap_line in sap_lines:
            if sap_line['Pax_Name'] == 'TF COST ITEM':
                sap_line_model.with_context(connector_no_export=True).create({
                    'send_date': sap_sale_order.send_date,
                    'sap_sale_order_id': sap_sale_order.id,
                    'sale_order_line_id':
                    sap_sale_order.sap_line_ids[0].sale_order_line_id.id,
                    'backend_id': sap_sale_order.backend_id.id,
                    'sap_line_detail': json.dumps(sap_line),
                })
                continue
            line = sap_line_model.browse(sap_line['external_id'])
            line.sap_line_detail = json.dumps(sap_line)

        if 'enett_payments' not in response:
            return

        sap_payment_model = self.env['ofh.payment.sap']
        enett_payments = response['enett_payments']

        for enett in enett_payments:
            values = {
                'send_date': sap_sale_order.send_date,
                'sap_sale_order_id': sap_sale_order.id,
                'backend_id': sap_sale_order.backend_id.id,
                'sap_payment_detail': json.dumps(enett.get('data')),
                'sap_xml': enett.get('xml'),
                'state': sap_sale_order.state,
            }
            if 'error' in enett:
                values['failing_reason'] = 'error',
                values['failing_text'] = enett['error']
                values['state'] = 'failed'
                values['sap_status'] = 'not_applicable'
            else:
                values['state'] = sap_sale_order.state
            sap_payment_model.with_context(
                connector_no_export=True).create(values)


class SAPBindingSaleOrderListener(Component):
    _name = 'sap.binding.sale.order.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['ofh.sale.order.sap']

    @skip_if(lambda self, *args, **kwargs:
             self.env.context.get('connector_no_export'))
    def on_record_create(self, record, fields=None):
        force = False
        if 'force_send' in self.env.context and self.env.context['force_send']:
            force = True
        record.with_delay().export_record(force=force)


class OfhSaleOrderSapAdapter(Component):
    _name = 'sap.sale.order.adapter'
    _inherit = 'sap.adapter'
    _apply_on = ['ofh.sale.order.sap']

    def create(self, data, visualize=False):
        try:
            sap_api = getattr(self.work, 'sap_api')
        except AttributeError:
            raise AttributeError(
                'You must provide a sap_api attribute with a '
                'SapApi instance to be able to use the '
                'Backend Adapter.'
            )
        if visualize:
            return sap_api.visualize_sale_order(data)

        return sap_api.send_sale_order(data)


class OfhPaymentSapExporter(Component):
    _name = 'sap.payment.exporter'
    _inherit = 'sap.exporter'
    _apply_on = ['ofh.payment.sap']

    def _must_skip(self, binding) -> str:
        # if any successful sending to SAP skip the sending.
        if binding.sap_payment_ids.filtered(lambda o: o.state == 'success'):
            return 'Already Sent'

        if binding._name == 'ofh.payment' and \
                not binding.order_id.is_payment_applicable:
            return "Not Applicable for Sending"

        return ''

    def run(self, sap_payment, force=False):
        binding = sap_payment.payment_id

        if not binding:
            binding = sap_payment.payment_request_id

        if not binding:
            raise MissingError("Missing binding.")

        skip_reason = self._must_skip(binding=binding)
        if skip_reason and not force and sap_payment.state != 'visualize':
            return sap_payment.write({
                'failing_reason': 'error',
                'failing_text': skip_reason,
                'state': 'failed',
                'sap_status': 'not_applicable',
            })

        payload = sap_payment._get_payment_payload()
        try:
            if sap_payment.state == 'visualize':
                result = self.backend_adapter.create(
                    data=payload, visualize=True)
            else:
                result = self.backend_adapter.create(data=payload)

        except HTTPError as e:
            if e.response.json().get('type', '') == RESOURCE_ERROR:
                failing_reason = 'skipped'
            else:
                failing_reason = 'error'

            return sap_payment.write({
                'failing_reason': failing_reason,
                'failing_text': e.response.json().get('message', ''),
                'state': 'failed',
                'sap_status': 'not_applicable',
            })

        self._after_export(sap_payment, response=result.json())

        return {"Success"}

    def _after_export(self, sap_payment, response):
        if not response:
            return

        update_values = {
            'failing_reason': 'not_applicable',
            'sap_xml': response.get('xml'),
            'sap_payment_detail': json.dumps(response.get('data')),
        }

        if sap_payment.state != 'visualize':
            update_values['state'] = 'success'
        else:
            update_values['sap_status'] = 'not_applicable'

        sap_payment.write(update_values)


class SAPBindingPaymentListener(Component):
    _name = 'sap.binding.payment.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['ofh.payment.sap']

    @skip_if(lambda self, *args, **kwargs:
             self.env.context.get('connector_no_export'))
    def on_record_create(self, record, fields=None):
        force = False
        if 'force_send' in self.env.context and self.env.context['force_send']:
            force = True
        record.with_delay().export_record(force=force)


class OfhPaymentSapAdapter(Component):
    _name = 'sap.payment.adapter'
    _inherit = 'sap.adapter'
    _apply_on = ['ofh.payment.sap']

    def create(self, data, visualize=False):
        try:
            sap_api = getattr(self.work, 'sap_api')
        except AttributeError:
            raise AttributeError(
                'You must provide a sap_api attribute with a '
                'SapApi instance to be able to use the '
                'Backend Adapter.'
            )
        if visualize:
            return sap_api.visualize_payment(data)

        return sap_api.send_payment(data)
