# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Bank Settlement',
    'description': """
        Synchronisation of payments from Bank Settlement""",
    'version': '13.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_hub_connector',
    ],
    'data': [
        # 'security/groups.xml',
        'views/ofh_bank_settlement.xml',
        'wizards/ofh_bank_settlement_import.xml',
    ],
    'demo': [
        # 'demo/ofh_bank_settlement.xml',
    ],
}
