# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Updating Matching status for existing payment requests.")
    cr.execute("""
        update ofh_supplier_invoice_line set active = False where
        invoice_date <= '2019-04-28';
    """)
