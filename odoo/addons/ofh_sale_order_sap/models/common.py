# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector_importer.log import logger
from odoo.addons.connector_importer.models.job_mixin import JobRelatedMixin


class SaleOrderSAPMapper(Component):
    _name = 'ofh.sale.order.sap.mapper'
    _inherit = 'importer.base.mapper'
    _apply_on = ['ofh.sale.order.sap']

    @mapping
    def sap_status(self, record) -> dict:
        sale_backend = self.env.ref(
            'ofh_sale_order_sap.sap_sale_import_backend')
        if self.backend_record == sale_backend:
            return {'sap_status': 'in_sap'}
        return {}


class SaleOrderSAPRecordImporter(Component):
    _name = 'sale.order.sap.record.importer'
    _inherit = 'importer.record'
    _apply_on = ['ofh.sale.order.sap']

    odoo_unique_key = 'booking_number'

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
        If the sale order matches a record we will update only the
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
                            "Record not found in Sale Orders."})
                return True
        except Exception as err:
            self.tracker.log_error(values, line, odoo_record, message=err)
            if self._break_on_error:
                raise err
            return False


class SaleOrderSAPHandler(Component):
    _name = 'sale.order.sap.handler'
    _inherit = 'importer.odoorecord.handler'
    _apply_on = ['ofh.sale.order.sap']

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the record in odoo."""
        return [
            ('state', '=', 'success'),
            (self.unique_key, '=',
             orig_values.get('Purchase Order Number'))]


class PaymentSAPMapper(Component):
    _name = 'ofh.payment.sap.mapper'
    _inherit = 'importer.base.mapper'
    _apply_on = ['ofh.payment.sap']

    @mapping
    def sap_status(self, record) -> dict:
        payment_backend = self.env.ref(
            'ofh_sale_order_sap.sap_payment_import_backend')
        if self.backend_record == payment_backend:
            return {'sap_status': 'in_sap'}
        return {}


class PaymentSAPRecordImporter(Component):
    _name = 'payment.sap.record.importer'
    _inherit = 'importer.record'
    _apply_on = ['ofh.payment.sap']

    odoo_unique_key = 'assignment'

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
        If the sale order matches a record we will update only the
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
                            "Record not found in Payments SAP."})
                return True
        except Exception as err:
            self.tracker.log_error(values, line, odoo_record, message=err)
            if self._break_on_error:
                raise err
            return False


class PaymentSAPHandler(Component):
    _name = 'payment.sap.handler'
    _inherit = 'importer.odoorecord.handler'
    _apply_on = ['ofh.payment.sap']

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the record in odoo."""
        return [
            ('state', '=', 'success'),
            (self.unique_key, '=',
             orig_values.get('Assignment'))]


class ImportRecordSet(models.Model, JobRelatedMixin):
    _inherit = 'import.recordset'

    @api.multi
    def run_import(self):
        self.ensure_one()
        va05_backend = self.env.ref(
            'ofh_sale_order_sap.sap_sale_import_backend')
        fbl5n_backend = self.env.ref(
            'ofh_sale_order_sap.sap_payment_import_backend')
        if self.backend_id in (va05_backend, fbl5n_backend):
            return self._run_import(channel='root.import.sap')
        return super(ImportRecordSet, self).run_import()


class ImportRecord(models.Model, JobRelatedMixin):
    _inherit = 'import.record'

    @api.multi
    def run_import(self):
        self.ensure_one()
        va05_backend = self.env.ref(
            'ofh_sale_order_sap.sap_sale_import_backend')
        fbl5n_backend = self.env.ref(
            'ofh_sale_order_sap.sap_payment_import_backend')
        if self.backend_id in (va05_backend, fbl5n_backend):
            return self._run_import(channel='root.import.sap')
        return super(ImportRecord, self).run_import()
