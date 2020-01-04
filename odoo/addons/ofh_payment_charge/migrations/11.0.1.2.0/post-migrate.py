# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Updating Payment Termenology Payment Charge Model.")
    cr.execute("""
        -- migrate op
        update ofh_payment_charge set payment_method=lower(payment_mode) where
        provider='op';
        -- update bank transfer string
        update ofh_payment_charge set payment_method='bank_transfer' where
        payment_method='bank transfer';
        -- loyalty
        update ofh_payment_charge set payment_method=provider where
        provider='loyalty';
        -- update loyalty provider as qitaf
        update ofh_payment_charge set provider='qitaf' where
        provider='loyalty';
        -- if it is mada
        update ofh_payment_charge set is_mada=true where
        card_type='mada';
        -- update card type
        update ofh_payment_charge set card_type=lower(payment_method) where
        payment_method in ('Visa', 'MasterCard', 'Amex');
        -- migrate online
        update ofh_payment_charge set payment_method='online' where
        provider in ('checkoutcom', 'fort', 'knet', 'tp');
    """)
    _logger.info("Done Updating Payment Termenology Payment Charge Model.")