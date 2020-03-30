# Copyright 2019 Seera Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Payment Reconciliation',
    'description': """
        Reconciliation of payment vs gateway vs settlement""",
    'version': '13.0.1.0.0',
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
        'ofh_sale_order_sap',
        'ofh_sale_order_payment_request',
    ],
    'data': [
        'security/groups.xml',
        'security/ofh_payment.xml',
        'security/ofh_payment_sap.xml',
        'security/ofh_payment_charge.xml',
        'security/ofh_payment_request.xml',
        'security/ofh_payment_gateway.xml',
        'security/ofh_payment_gateway_line.xml',
        'security/ofh_sale_order_sap.xml',
        'security/ofh_bank_settlement.xml',
        'wizards/ofh_payment_loader.xml',
        'wizards/ofh_bank_settlement_force_match.xml',
        'wizards/ofh_payment_gateway_force_match.xml',
        'wizards/ofh_payment_reconciliation_tag.xml',
        'views/ofh_bank_settlement.xml',
        'views/ofh_payment_gateway.xml',
        'views/ofh_payment_request.xml',
        'views/ofh_payment.xml',
        'views/menus.xml',
    ],
    'demo': [
    ],
}
