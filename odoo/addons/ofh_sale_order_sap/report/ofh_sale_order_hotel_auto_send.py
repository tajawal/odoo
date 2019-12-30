# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, tools


class OfhSaleOrderAutoSend(models.Model):
    _name = 'ofh.sale.order.hotel.auto.send'
    _description = "Hotels Sales Orders to be auto sent"
    _auto = False

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'ofh_sale_order_hotel_auto_send')
        self._cr.execute("""
            create view ofh_sale_order_hotel_auto_send as (
                SELECT id
                FROM ofh_sale_order
                WHERE
                    is_sale_applicable = true AND
                    order_reconciliation_status != 'unreconciled' AND
                    updated_at <= (date(CURRENT_DATE::date - '1 day'::interval) || ' 23:59:59')::timestamp AND
                    updated_at >= (date(CURRENT_DATE::date - '4 day'::interval) || ' 00:00:00')::timestamp AND
                    order_type = 'hotel' AND
                    is_voided = false AND
                    paid_at is not null AND
                    -- Booking must have lines.
                    EXISTS (
                        SELECT order_id
                        FROM ofh_sale_order_line)

                -- Not sent to SAP
                EXCEPT
                    SELECT sale_order_id as id
                    FROM ofh_sale_order_sap WHERE
                    state = 'success' AND sale_order_id > 0
            )

        """)
