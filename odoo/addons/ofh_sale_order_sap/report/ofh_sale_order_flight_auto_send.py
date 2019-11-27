# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, tools


class OfhSaleOrderAutoSend(models.Model):
    _name = 'ofh.sale.order.flight.auto.send'
    _description = "Flights Sales Orders to be auto sent"
    _auto = False

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'ofh_sale_order_auto_send')
        tools.drop_view_if_exists(self._cr, 'ofh_sale_order_flight_auto_send')
        self._cr.execute("""
            create view ofh_sale_order_flight_auto_send as (
                SELECT id
                FROM ofh_sale_order
                WHERE is_sale_applicable = true AND
                    order_reconciliation_status != 'unreconciled' AND
                    created_at <= (date(CURRENT_DATE::date - '1 day'::interval) || ' 23:59:59')::timestamp AND
                    created_at >= (date(CURRENT_DATE::date - '4 day'::interval) || ' 00:00:00')::timestamp AND
                    order_type = 'flight' AND
                    paid_at is not null AND

                    -- Only applicable office ids.
                    upper(ticketing_office_id) not in
                    ('CAI3T38EH', 'CAIEG21Q4', '87OF', '8RR9', 'GALILEO') AND
                    is_voided = false AND

                    -- flight booking should be paid.
                    EXISTS (
                        SELECT order_id
                        FROM ofh_payment
                        WHERE payment_status in ('11111', '10000', '10100'))

                -- Not sent to SAP
                EXCEPT
                    SELECT sale_order_id as id
                    FROM ofh_sale_order_sap WHERE
                    state = 'success' AND sale_order_id > 0
            )

        """)
