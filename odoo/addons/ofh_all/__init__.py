# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init(cr, registry):
    """Active all currencies in Odoo.

    In Odoo all the currencies are preset to inactive, but in Ayesha we
    need all the currencies to be active, with this post init hook, all
    currencies will be active at the first installation of the instance
    """
    cr.execute(
        "update res_currency set active = True")
    cr.execute(
        "update res_currency set symbol= 'AED' where id = 131")
    cr.execute(
        "update res_currency set symbol= 'SAR' where id=154")
    cr.execute(
        "update res_currency set symbol= 'KWD' where id=97")
    cr.execute(
        "update res_currency set symbol= 'EGP' where id=77")
