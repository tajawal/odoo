# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
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

    @api.multi
    def generate_loader(self):
        payments = self._get_eligible_payments()
        response = []
        if payments:
            params = self._prepare_loader_params(payments)
            sap_api = SapXmlApi()
            response = sap_api.generate_loader(params)

        return response

    def _get_eligible_payments(self):
        if self.is_apple_pay:
            apply_pay_condition = f"AND pg.is_apple_pay={self.is_apple_pay}"
        else:
            apply_pay_condition = ""

        self.env.cr.execute(f"""
                    SELECT pg.*, 
                           p.mid,
                           p.total_amount, 
                           p.assignment       AS assignment, 
                           bs.settlement_date AS settlement_date, 
                           so.name            AS order_number 
                    FROM   ofh_payment_gateway AS pg 
                           JOIN ofh_payment AS p 
                             ON pg.hub_payment_id = p.id 
                           JOIN ofh_bank_settlement AS bs 
                             ON pg.bank_settlement_id = bs.id 
                           JOIN ofh_sale_order AS so 
                             ON p.order_id = so.id 
                    WHERE  pg.settlement_matching_status = 'matched' 
                           AND pg.reconciliation_status = 'reconciled' 
                           AND pg.entity = '{self.entity}' 
                           AND pg.acquirer_bank = '{self.bank_name}' 
                           AND pg.provider = '{self.provider}'
                           {apply_pay_condition} 
                           AND p.currency_id = {self.currency_id.id} 
                           AND bs.settlement_date = '{self.settlement_date}' 
                """)
        payments = self.env.cr.dictfetchall()
        return payments

    def _prepare_loader_params(self, payments):
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
                "mid": payment["mid"]
            }
            data.append(p_params)

        params.update({"data": data})
        return params
