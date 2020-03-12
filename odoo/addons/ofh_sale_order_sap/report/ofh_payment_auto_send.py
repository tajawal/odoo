# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, tools


class OfhPaymentAutoSend(models.Model):
    _name = 'ofh.payment.auto.send'
    _description = "Payments to be auto sent"
    _auto = False

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'ofh_payment_auto_send')
        self._cr.execute("""
            CREATE VIEW ofh_payment_auto_send AS (
                SELECT
                    id
                FROM
                    ofh_payment
                WHERE
                (
                    (
                      payment_method = 'online' AND
                      payment_status IN ('11111', '10000', '83027')
                    )
                OR 
                    (
                      payment_method = 'loyalty' AND
                      payment_status IN ('11111', '10000')
                    )
                OR 
                    (
                      payment_method NOT IN ('online', 'loyalty') AND store_id = '1000'
                    )
                )
                AND
                    created_at >= (date(CURRENT_DATE::date - '4 day'::interval) || ' 00:00:00')::timestamp
                AND
                    is_payment_applicable = true
                EXCEPT
                    SELECT payment_id as id
                    FROM ofh_payment_sap
                    WHERE state = 'success' AND payment_id > 0
            )
        """)
