# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector_importer.log import logger


class PaymentRequestSAPMapper(Component):
    _name = 'ofh.payment.request.sap.mapper'
    _inherit = 'importer.base.mapper'
    _apply_on = ['ofh.payment.request']

    @mapping
    def sap_status(self, record) -> dict:
        payment_backend = self.env.ref(
            'ofh_payment_request_sap.sap_payment_import_backend')
        sale_backend = self.env.ref(
            'ofh_payment_request_sap.sap_sale_import_backend')
        if self.backend_record == sale_backend:
            return {'sap_status': 'sale_in_sap'}
        elif self.backend_record == payment_backend:
            return {'sap_status': 'payment_in_sap'}
        return {}


class PaymentRequestSAPRecordImporter(Component):
    _name = 'payment.request.sap.record.importer'
    _inherit = 'importer.record'
    _apply_on = ['ofh.payment.request']

    odoo_unique_key = 'sap_xml_sale_ref'

    def skip_it(self, values, origin_values) -> dict:
        """ Return True if the line document type is different that
        'DA' or 'DB'. this is applied only for SAP payment report.

        Arguments:
            values {dict} -- Mapped values
            origin_values {dict} -- Original raw data.
        """

        if origin_values.get('Document type') not in ('DA', 'DB'):
            return {'message': "Document type not applicable"}
        return {}

    def run(self, record, **kw):
        """
        If the payment request matches a record we will update only the
        SAP Status otherwise we don't do anything.
        Mark the lines that didn't match any odoo record as skipped.
        """
        self.record = record
        if not self.record:
            return
        self._init_importer(self.record.recordset_id)
        for line in self._record_lines():
            self._import_line(line)
        # log chunk finished
        msg = ' '.join([
            '{} import chunk completed'.format(
                self.tracker.log_prefix.upper()),
            '[created: {created}]',
            '[updated: {updated}]',
            '[skipped: {skipped}]',
            '[errored: {errored}]',
        ]).format(**self.tracker.get_counters())
        self.tracker._log(msg)
        return self.env.user.notify_info(msg)

    def _import_line(self, line):
        line = self.prepare_line(line)
        options = self._load_mapper_options()

        odoo_record = None

        try:
            with self.env.cr.savepoint():
                values = self.mapper.map_record(line).values(**options)
            logger.debug(values)
        except Exception as err:
            values = {}
            self.tracker.log_error(values, line, odoo_record, message=err)
            if self._break_on_error:
                raise err
            return False
        try:
            with self.env.cr.savepoint():
                if self.record_handler.odoo_exists(values, line):
                    odoo_record = self.record_handler.odoo_write(values, line)
                    self.tracker.log_updated(values, line, odoo_record)
                else:
                    self.tracker.log_skipped(
                        values, line,
                        {'message':
                            "Record not found in Payment requests."})
                return True
        except Exception as err:
            self.tracker.log_error(values, line, odoo_record, message=err)
            if self._break_on_error:
                raise err
            return False


class PaymentRequestSAPHandler(Component):
    _name = 'payment.request.sap.handler'
    _inherit = 'importer.odoorecord.handler'
    _apply_on = ['ofh.payment.request']

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the record in odoo."""
        domain = [('integration_status', '!=', 'not_sent')]
        payment_backend = self.env.ref(
            'ofh_payment_request_sap.sap_payment_import_backend')
        sale_backend = self.env.ref(
            'ofh_payment_request_sap.sap_sale_import_backend')
        if self.backend_record == payment_backend:
            domain.append(
                ('sap_xml_file_ref', '=', orig_values.get('Assignment')))
        elif self.backend_record == sale_backend:
            domain.append(
                (self.unique_key, '=',
                 orig_values.get('Purchase Order Number')))
        return domain
