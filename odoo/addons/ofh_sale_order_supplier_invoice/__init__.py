import logging

from . import models, wizards

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):

    _logger.info("Updating Matching status for existing supplier lines.")

    cr.execute("""
        update ofh_supplier_invoice_line set matching_status = 'pr_matched'
        where state in ('forced', 'matched', 'suggested');
        update ofh_supplier_invoice_line set matching_status = 'unmatched'
        where state in ('ready', 'not_matched');
    """)

    _logger.info("Updating Reconciliation Status for existing supplier lines.")

    cr.execute("""
        update ofh_supplier_invoice_line
        set reconciliation_status = 'not_applicable'
        where invoice_date <= '2018-03-28';
    """)

    _logger.info(
        "Updating Reconciliation Status for existing Payment Requests.")

    cr.execute("""
        update ofh_payment_request set
        reconciliation_status = 'not_applicable';
    """)
