# Copyright 2019 Seera Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Bank Settlement Mashreq',
    'description': """
        Mashreq Bank Settlement Report Import.""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Seera Group',
    'website': 'https://seera.sa',
    'depends': [
        'ofh_hub_connector',
        'ofh_bank_settlement',
    ],
    'data': [
        'data/backend.xml',
        'views/ofh_bank_settlement.xml',
        'wizards/ofh_payment_gateway_import.xml'
    ],
    'demo': [
    ],
}
