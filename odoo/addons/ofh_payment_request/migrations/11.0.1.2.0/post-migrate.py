# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Updating Matching status for existing payment requests.")
    cr.execute("""
        update ofh_payment_request set matching_status = 'unmatched' where
        reconciliation_status = 'investigate';
        update ofh_payment_request set matching_status = 'matched' where
        reconciliation_status = 'matched';
        update ofh_payment_request set matching_status = 'not_applicable' where
        reconciliation_status = 'not_applicable';
    """)
