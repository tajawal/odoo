# Copyright 2019 Tajwal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import csv
import json

from odoo import api, models


class CommandCrypticReporter(models.AbstractModel):

    _name = 'reporter.command_cryptic'
    _inherit = 'reporter.mixin'
    report_extension = '.csv'

    report_keys = ['skipped', 'errored']
    report_group_by_status = True

    @api.model
    def report_get_writer(self, fileout, columns,
                          delimiter=',', quotechar='"'):
        writer = csv.DictWriter(
            fileout, columns,
            delimiter=delimiter,
            quoting=csv.QUOTE_NONNUMERIC,
            quotechar=quotechar)
        writer.writeheader()
        return writer

    @api.model
    def report_get_columns(self, recordset, orig_content, extra_keys=None):
        if orig_content:
            return [key for key in orig_content[0].keys()] + extra_keys
        return extra_keys

    @api.model
    def report_get_origin_content(self, recordset):
        if not recordset:
            return []
        records = recordset.get_records()
        if not records:
            return []
        lines = []
        for record in records:
            if not record.jsondata:
                continue
            lines.extend(json.loads(record.jsondata))
        return lines

    @api.model
    def report_add_line(self, writer, item):
        writer.writerow(item)

    @api.model
    def report_do(self, recordset, fileout, **options):
        """Produce report."""
        json_report = recordset.get_report()
        report_keys = options.get('report_keys', self.report_keys)
        group_by_status = options.get(
            'group_by_status', self.report_group_by_status)

        model_keys = [
            x for x in json_report.keys() if not x.startswith('_')]

        extra_keys = [
            self._report_make_key(x) for x in report_keys
        ]
        if not group_by_status:
            # we produce one column per-model per-status
            for model in model_keys:
                for key in report_keys:
                    extra_keys.append(self._report_make_key(key, model=model))

        orig_content = self.report_get_origin_content(recordset)
        columns = self.report_get_columns(
            recordset, orig_content, extra_keys=extra_keys)
        writer = self.report_get_writer(fileout, columns)

        self._report_do(
            json_report=json_report,
            reader=orig_content,
            writer=writer,
            model_keys=model_keys,
            report_keys=report_keys,
            group_by_status=group_by_status
        )

    @api.model
    def _report_do(
            self,
            json_report=None,
            reader=None,
            writer=None,
            model_keys=None,
            report_keys=None,
            group_by_status=True):

        line_handler = self._report_line_by_model_and_status
        if group_by_status:
            line_handler = self._report_line_by_status

        grouped = self._report_group_by_line(
            json_report, model_keys, report_keys)

        for line in reader:
            line_handler(line, line.get('_line_nr'), grouped, model_keys)
            self.report_add_line(writer, line)

    def _report_make_key(self, key, model=''):
        if model:
            return '[R] {}: {}'.format(model, key)
        return '[R] {}'.format(key)

    def _report_group_by_line(self, json_report, model_keys, report_keys):
        """Group report items by line number.

        Return something like:

        {
            'errored': {},
            'skipped': {
                2: [
                    {
                        u'line_nr': 2,
                        u'message': u'MISSING REQUIRED KEY=foo',
                        u'model': u'product.supplierinfo',
                        u'odoo_record': None
                    },
                    {
                        u'line_nr': 2,
                        u'message': u'MISSING REQUIRED KEY=bla',
                        u'model': u'product.product',
                        u'odoo_record': None
                    },
                ],
                3: [
                    {
                        u'line_nr': 3,
                        u'message': u'MISSING REQUIRED KEY=foo',
                        u'model': u'product.template',
                        u'odoo_record': None
                    },
                    {
                        u'line_nr': 3,
                        u'message': u'ALREADY_EXISTS code=XXXX',
                        u'model': u'product.product',
                        u'odoo_record': None
                    },
                ],
        }
        """
        by_line = {}
        for model in model_keys:
            # list of messages
            by_model = json_report.get(model, {})
            for key in report_keys:
                by_line.setdefault(key, {})
                for item in by_model.get(key, []):
                    by_line[key].setdefault(
                        item['line_nr'], []
                    ).append(item)
        return by_line

    def _report_line_by_model_and_status(
            self, line, line_num, grouped, model_keys):
        """Get one column per each pair model-status."""
        for model in model_keys:
            for status, lines in grouped.items():
                # get info on current line if any
                line_info = lines.get(line_num, {})
                # add the extra report column anyway
                line[self._report_make_key(model, status)] = \
                    line_info.get('message')

    def _report_line_by_status(
            self, line, line_num, grouped, model_keys):
        """Get one column per each status containing all modelss messages."""
        for status, by_line in grouped.items():
            line_info = by_line.get(line_num, [])
            line[self._report_make_key(status)] = '\n'.join([
                '{model}: {message}'.format(**item) for item in line_info
            ])
