# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from ..components.backend_adapter import SapXmlApi

import csv


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

    @api.multi
    def generate_loader(self):
        payments = self._get_eligible_payments()
        payment_requests = self._get_eligible_payment_requests()
        response = []
        if payments:
            params = self._prepare_loader_params(payments, payment_requests)
            sap_api = SapXmlApi()
            response = sap_api.generate_loader(params)
            if response:
                self.generate_loader_csv(response['payment_loader'])

        return response

    def _get_eligible_payments(self):
        apply_pay_condition = ""
        if self.entity == 'tajawal':
            if self.is_apple_pay:
                apply_pay_condition = f"AND pg.is_apple_pay={self.is_apple_pay}"
            else:
                apply_pay_condition = f"AND pg.is_apple_pay=False"

        query = f"""
                    SELECT pg.*, 
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
                    SELECT pg.*, 
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
        csv_columns = self.get_csv_headers()

        csv_file = f"{self.entity}_{self.provider}_{self.bank_name}_{self.currency_id.name}.csv"
        try:
            with open(csv_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for row_data in response:
                    writer.writerow(row_data)
        except IOError:
            print("I/O error")

        return {
            'name': 'Report',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=" + self._name + "&id=" + str(
                self.id) + "&filename_field=file_name&field=data_file&download=true&filename=" + csv_file,
            'target': 'self',
        }

    def get_csv_headers(self):
        return [
            "HEADER",
            "SequencenumberHeader",
            "CompanyCode",
            "DocumentType",
            "DocumentDate",
            "PostingDate",
            "DocumentHeaderText",
            "CurrencyCode",
            "Headerreference",
            "AP ITEM",
            "SequencenumberItem",
            "Vendor",
            "DebitCreditPostingKey",
            "DocumentCurrencyAmount",
            "LocalCurrencyAmount",
            "CostCenter",
            "ProfitCenter",
            "InternalOrder",
            "WBSElement",
            "Taxcode",
            "LineItemText",
            "Referencekey1",
            "Referencekey2",
            "Referencekey3",
            "Assignment",
            "PaymentMethod",
            "Paymentblock"
        ]
