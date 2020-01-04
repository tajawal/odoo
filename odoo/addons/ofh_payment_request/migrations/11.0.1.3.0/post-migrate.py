# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Updating Group Id for existing payment requests.")
    cr.execute("""
        update hub_payment_request set group_id = track_id;
    """)
