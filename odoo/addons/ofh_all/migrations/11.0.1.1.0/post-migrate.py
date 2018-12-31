# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Updating Currencies symbol to be the same as the name.")
    cr.execute("update res_currency set symbol = name;")
