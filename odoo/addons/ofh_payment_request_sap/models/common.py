# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector_importer.log import logger


####################
# SAP SALE REPORT
####################


class PaymentRequestSAPSaleMapper(Component):
    _name = 'ofh.payment.request.sap.sale.mapper'
    _inherit = 'importer.base.mapper'
    _apply_on = ['ofh.payment.request']

    @mapping
    def sap_status(self, record):
        return {'sap_status': 'sale_in_sap'}


class PaymentRequestSAPSaleRecordImporter(Component):
    _name = 'payment.request.sap.record.importer'
    _inherit = 'importer.record'
    _apply_on = ['ofh.payment.request']

    odoo_unique_key = 'sap_xml_sale_ref'

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
                    raise
                continue

            try:
                with self.env.cr.savepoint():
                    if self.record_handler.odoo_exists(values, line):
                        odoo_record = \
                            self.record_handler.odoo_write(values, line)
                        self.tracker.log_updated(values, line, odoo_record)
                    else:
                        self.tracker.log_skipped(
                            values, line,
                            "Record not found in Payment requests.")
                        continue
            except Exception as err:
                self.tracker.log_error(values, line, odoo_record, message=err)
                if self._break_on_error:
                    raise
                continue


class PaymentRequestSAPSaleHandler(Component):
    _name = 'payment.request.sap.sale.handler'
    _inherit = 'importer.odoorecord.handler'
    _apply_on = ['ofh.payment.request']

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the record in odoo."""
        return [
            ('integration_status', 'in', ['sale_sent', 'sale_payment_sent']),
            (self.unique_key, '=', values.get('Purchase Order Number'))]


######################
# SAP PAYMENT REPORT
######################


class PaymentRequestSAPPaymentMapper(Component):
    _name = 'ofh.payment.request.sap.payment.mapper'
    _inherit = 'importer.base.mapper'
    _apply_on = ['ofh.payment.request']


class PaymentRequestSAPPaymentRecordImporter(Component):
    _name = 'payment.request.sap.payment.record.importer'
    _inherit = 'importer.record'
    _apply_on = ['ofh.payment.request']

    odoo_unique_key = 'sap_xml_sale_ref'

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
                    raise
                continue

            try:
                with self.env.cr.savepoint():
                    if self.record_handler.odoo_exists(values, line):
                        odoo_record = \
                            self.record_handler.odoo_write(values, line)
                        self.tracker.log_updated(values, line, odoo_record)
                    else:
                        self.tracker.log_skipped(
                            values, line,
                            "Record not found in Payment requests.")
                        continue
            except Exception as err:
                self.tracker.log_error(values, line, odoo_record, message=err)
                if self._break_on_error:
                    raise
                continue


class PaymentRequestSAPPaymentHandler(Component):
    _name = 'payment.request.sap.payment.handler'
    _inherit = 'importer.odoorecord.handler'
    _apply_on = ['ofh.payment.request']

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the record in odoo."""
        return [
            ('integration_status', 'in',
             ['payment_sent', 'sale_payment_sent']),
            (self.unique_key, '=', values.get('Purchase Order Number'))]
