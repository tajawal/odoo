# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Payment',
    'description': """
        Synchronisation of payment from HUB""",
    'version': '13.0.1.2.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_hub_connector',
        'ofh_mail_activity',
        'ofh_base_currency',
        'ofh_payment_charge',
    ],
    'data': [
        'views/ofh_payment.xml',
    ],
    'demo': [
        'demo/ofh_payment.xml',
        'demo/ofh_payment_charge.xml',
    ],
}
