# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Payment Charge',
    'description': """
        Synchronisation of payment charge from HUB""",
    'version': '11.0.1.1.1',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_hub_connector',
        'ofh_base_currency',
    ],
    'data': [
        'views/ofh_payment_charge.xml',
    ],
    'demo': [
        'demo/ofh_payment_charge.xml',
    ]
}
