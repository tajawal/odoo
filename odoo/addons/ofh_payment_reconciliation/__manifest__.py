# Copyright 2019 Seera Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Payment Reconciliation',
    'description': """
        Reconciliation of payment vs gateway vs settlement""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Seera Group',
    'website': 'https://seera.sa',
    'depends': [
        'ofh_payment_gateway',
        'ofh_payment_gateway_checkout',
        'ofh_payment_gateway_fort',
        'ofh_payment_gateway_knet',
        'ofh_bank_settlement',
        'ofh_bank_settlement_sabb',
        'ofh_bank_settlement_mashreq',
        'ofh_bank_settlement_rajhi',
        'ofh_bank_settlement_amex',
        'ofh_payment',
        'ofh_payment_request',
    ],
    'data': [
        'wizards/ofh_payment_reconciliation_tag.xml',
        'views/ofh_bank_settlement.xml',
        'views/ofh_payment_gateway.xml',
        'views/ofh_payment.xml',
        'views/menus.xml',
    ],
    'demo': [
    ],
}
