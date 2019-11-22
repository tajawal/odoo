# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import csv

from odoo import _, api, fields, models

from ..components.backend_adapter import SapXmlApi


class OfhPaymentLoader(models.TransientModel):
    _name = 'ofh.payment.loader'

    entity = fields.Selection(
        selection=[
            ('almosafer', 'Almosafer'),
            ('tajawal', 'Tajawal')],
        default="almosafer",
        required=True
    )
    bank_name = fields.Selection(
        string="Bank Name",
        selection=[
            ('mashreq', 'Mashreq'),
            ('sabb', 'SABB'),
            ('rajhi', 'Rajhi'),
            ('knet', 'Knet'),
            ('amex', 'Amex')],
        required=True
    )
    provider = fields.Selection(
        string="Provider",
        selection=[
            ('checkout', 'Checkout'),
            ('fort', 'Fort'),
            ('knet', 'Knet'),
        ],
        required=True
    )
    settlement_date = fields.Date(
        string="Settlement Date",
        required=True
    )
    is_apple_pay = fields.Boolean(
        string="Apple Pay?",
        default=False,
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True
    )
    download_file = fields.Binary(
        string="Upload File",
    )
    file_name = fields.Char(
        string="File Name",
    )

    @api.multi
    def generate_loader(self):
        payments = self._get_eligible_payments()
        payment_requests = self._get_eligible_payment_requests()
        url = ''
        if payments:
            params = self._prepare_loader_params(payments, payment_requests)
            sap_api = SapXmlApi()
            response = sap_api.generate_loader(params)
            if response:
                url = self.generate_loader_csv(response['payment_loader'])

            action = {
                'name': 'Go to Download URL',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target': 'self',
                'url': url,
            }
            return action

    def _get_eligible_payments(self):
        apply_pay_condition = ""
        if self.entity == 'tajawal':
            if self.is_apple_pay:
                apply_pay_condition = f"AND pg.is_apple_pay={self.is_apple_pay}"
            else:
                apply_pay_condition = f"AND pg.is_apple_pay=False"

        query = f"""
                    SELECT pg.payment_status as payment_status,
                           pg.auth_code as auth_code,
                           p.mid,
                           p.total_amount,
                           p.assignment       AS assignment,
                           bs.settlement_date AS settlement_date,
                           bs.net_transaction_amount AS net_transaction_amount,
                           bs.merchant_charge_amount AS merchant_charge_amount,
                           bs.merchant_charge_vat AS merchant_charge_vat,
                           so.name            AS order_number
                    FROM   ofh_payment_gateway AS pg
                           JOIN ofh_payment AS p
                             ON pg.hub_payment_id = p.id
                           JOIN ofh_bank_settlement AS bs
                             ON pg.bank_settlement_id = bs.id
                           JOIN ofh_sale_order AS so
                             ON p.order_id = so.id
                    WHERE  p.pg_matching_status = 'matched' and pg.settlement_matching_status = 'matched'
                           AND pg.reconciliation_status = 'reconciled'
                           AND pg.entity = '{self.entity}'
                           AND pg.acquirer_bank = '{self.bank_name}'
                           AND pg.provider = '{self.provider}'
                           {apply_pay_condition}
                           AND p.currency_id = {self.currency_id.id}
                           AND bs.settlement_date = '{self.settlement_date}'
                           AND p.assignment <> '' 
                """
        self.env.cr.execute(query)
        payments = self.env.cr.dictfetchall()
        return payments

    def _get_eligible_payment_requests(self):
        apply_pay_condition = ""
        if self.entity == 'tajawal':
            if self.is_apple_pay:
                apply_pay_condition = f"AND pg.is_apple_pay={self.is_apple_pay}"
            else:
                apply_pay_condition = f"AND pg.is_apple_pay=False"

        query = f"""
                    SELECT pg.payment_status as payment_status,
                           pg.auth_code as auth_code,
                           c.mid,
                           p.total_amount,
                           p.assignment       AS assignment,
                           bs.settlement_date AS settlement_date,
                           bs.net_transaction_amount AS net_transaction_amount,
                           bs.merchant_charge_amount AS merchant_charge_amount,
                           bs.merchant_charge_vat AS merchant_charge_vat,
                           so.name            AS order_number
                    FROM   ofh_payment_gateway AS pg
                           JOIN ofh_payment_request AS p
                             ON pg.hub_payment_request_id = p.id
                           JOIN ofh_payment_charge AS c
                             ON pg.hub_payment_request_id = c.payment_request_id
                           JOIN ofh_bank_settlement AS bs
                             ON pg.bank_settlement_id = bs.id
                           JOIN ofh_sale_order AS so
                             ON p.order_id = so.id
                    WHERE  p.pg_matching_status = 'matched' and pg.settlement_matching_status = 'matched'
                           AND pg.reconciliation_status = 'reconciled'
                           AND pg.entity = '{self.entity}'
                           AND pg.acquirer_bank = '{self.bank_name}'
                           AND pg.provider = '{self.provider}'
                           {apply_pay_condition}
                           AND p.currency_id = {self.currency_id.id}
                           AND bs.settlement_date = '{self.settlement_date}'
                           AND p.assignment <> '' 
                """
        self.env.cr.execute(query)
        payments = self.env.cr.dictfetchall()
        return payments

    def _prepare_loader_params(self, payments, payment_requests):
        params = {
            "entity": self.entity,
            "bank_name": self.bank_name,
            "payment_gateway": self.provider,
            "settlement_date": self.settlement_date,
            "currency": self.currency_id.name,
            "is_apple_pay": self.is_apple_pay,
        }

        data = []
        for payment in payments:
            p_params = {
                "order_number": payment["order_number"],
                "payment_status": payment["payment_status"],
                "total": payment["total_amount"],
                "assignment": payment["assignment"],
                "auth_code": payment["auth_code"],
                "mid": payment["mid"],
                "net_transaction_amount": payment["net_transaction_amount"],
                "merchant_charge_amount": payment["merchant_charge_amount"],
                "merchant_charge_vat": payment["merchant_charge_vat"]
            }
            data.append(p_params)

        for payment_request in payment_requests:
            p_params = {
                "order_number": payment_request["order_number"],
                "payment_status": payment_request["payment_status"],
                "total": payment_request["total_amount"],
                "assignment": payment_request["assignment"],
                "auth_code": payment_request["auth_code"],
                "mid": payment_request["mid"],
                "net_transaction_amount": payment_request["net_transaction_amount"],
                "merchant_charge_amount": payment_request["merchant_charge_amount"],
                "merchant_charge_vat": payment_request["merchant_charge_vat"]
            }
            data.append(p_params)

        params.update({"data": data})
        return params

    @api.multi
    def generate_loader_csv(self, response):
        self.ensure_one()
        csv_columns = self.get_csv_headers()

        csv_file = f"{self.entity}_{self.provider}_{self.bank_name}_{self.currency_id.name}.csv"
        import io
        import csv
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(csv_columns)
        for row_data in response:
            row = self.get_dict_values(row_data)
            writer.writerow(row)

        data = output.getvalue()

        self.write({
            'download_file': base64.encodestring(data.encode()),
            'file_name': csv_file,
        })

        url = f"web/content/?model=ofh.payment.loader&id={self.id}&filename_field=file_name&field=download_file&download=true&filename={csv_file}"
        return url

    @api.multi
    def get_dict_values(self, row_data):
        return [
            row_data.get('HEADER'),
            row_data.get('Sequence number Header'),
            row_data.get('Company Code'),
            row_data.get('Document Type'),
            row_data.get('Document Date'),
            row_data.get('Posting Date'),
            row_data.get('Document Header Text'),
            row_data.get('Currency Code'),
            row_data.get('Header reference'),
            row_data.get('AP ITEM'),
            row_data.get('Sequence number Item'),
            row_data.get('Vendor'),
            row_data.get('Debit Credit Posting Key'),
            row_data.get('Document Currency Amount'),
            row_data.get('Local Currency Amount'),
            row_data.get('Cost Center'),
            row_data.get('Profit Center'),
            row_data.get('Internal Order'),
            row_data.get('WBS Element'),
            row_data.get('Tax code'),
            row_data.get('Line Item Text'),
            row_data.get('Reference key 1'),
            row_data.get('Reference key 2'),
            row_data.get('Reference key 3'),
            row_data.get('Assignment'),
            row_data.get('Payment Method'),
            row_data.get('Payment block')
        ]

    @api.multi
    def get_csv_headers(self):
        return [
            'HEADER',
            'Sequence number',
            'Company Code',
            'Document Type',
            'Document Date',
            'Posting Date',
            'Document Header Text',
            'Currency Code',
            'Header reference',
            'AP ITEM',
            'Sequence number',
            'Vendor',
            'Debit Credit Posting Key',
            'Document Currency Amount',
            'Local Currency Amount',
            'Cost Center',
            'Profit Center',
            'Internal Order',
            'WBS Element',
            'Tax code',
            'Line Item Text',
            'Reference key 1',
            'Reference key 2',
            'Reference key 3',
            'Assignment',
            'Payment Method',
            'Payment block'
        ]
