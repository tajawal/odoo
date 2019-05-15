# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo.api import SUPERUSER_ID, Environment

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Updating Order Reconciliation Status.")

    cr.execute("""
    UPDATE ofh_sale_order set order_reconciliation_status = 'reconciled'
    FROM ofh_sale_order o
    WHERE
        NOT EXISTS (
            SELECT order_id
            FROM ofh_sale_order_line l
            WHERE l.order_id = o.id AND
                  l.matching_status = 'matched' AND
                  l.reconciliation_status in ('unreconciled', 'not_applicable')
        )
        AND o.order_type = 'flight';
    """)

    _logger.info("Updating Payment Request Reconciliation Status.")
    env = Environment(cr, SUPERUSER_ID, {})

    payment_requests = env['ofh.payment.request'].search([
        ('request_type', '=', 'refund'), ('matching_status', '=', 'matched'),
        ('updated_at', '>=', '2019-05-01 00:00:00')])

    if payment_requests:
        payment_requests._compute_reconciliation_amount()
