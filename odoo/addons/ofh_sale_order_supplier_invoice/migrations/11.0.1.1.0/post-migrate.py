# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import api, SUPERUSER_ID


_logger = logging.getLogger(__name__)


def migrate(cr, version):

    env = api.Environment(cr, SUPERUSER_ID, {})
    sale_orders = env['ofh.sale.order'].search([
        ('create_date', '>=', '2019-05-01 00:00:00'),
        ('order_type', '=', 'flight')])

    if sale_orders:
        _logger.info("Updating Order Reconciliation Statuses.")
        sale_orders._compute_order_reconciliation_status()
        _logger.info("Updating Payment Request Reconciliation Statuses.")
        sale_orders._compute_payment_request_reconciliation_status()
        _logger.info("Updating Payment Request Matching Statuses.")
        sale_orders._compute_payment_request_matching_status()
