# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "odoo_finance_hub",
    'description': """
        Odoo aplication for odoo_finance_hub""",
    'author': 'ACSONE SA/NV',
    'website': "http://acsone.eu",
    'category': 'odoo_finance_hub',
    'version': '11.0.2.6.20',
    'license': 'AGPL-3',
    'depends': [
        # odoo_finance_hub open source addons
        'ofh_base_currency',
        'ofh_payment_request_invoice',
        'ofh_payment_request_sap_s3_bucket',
        'ofh_sale_order_supplier_invoice_gds',
        'ofh_sale_order_supplier_invoice_tf',
        'ofh_sale_order_supplier_invoice_enett',
        'ofh_sale_order_supplier_invoice_nile',
        'ofh_sale_order_supplier_invoice_itl',
        'ofh_sale_order_supplier_invoice_tv',
        'ofh_sale_order_sap',
        'ofh_sale_order_sap_gds',
        'ofh_sale_order_sap_tf',
        'ofh_sale_order_sap_enett',
        'ofh_sale_order_sap_itl',
        'ofh_sale_order_sap_tv',
        # Payment Gateway Addons
        'ofh_payment_gateway',
        'ofh_payment_gateway_checkout',
        'ofh_payment_gateway_fort',
        'ofh_payment_gateway_knet',
        'ofh_payment_reconciliation',
        # Bank Settlement
        'ofh_bank_settlement',
        'ofh_bank_settlement_sabb',
        'ofh_bank_settlement_mashreq',
        'ofh_bank_settlement_rajhi',
        'ofh_bank_settlement_amex',
        # Payment Reconciliation
        'ofh_payment_reconciliation',
        # !!! no odoo enterprise addons dependencies !!!
        # OCA/server-tools
        'base_optional_quick_create',
        'mail_environment',
        'module_auto_update',
        'server_environment_ir_config_parameter',
        # OCA/web
        'web_dialog_size',
        'web_environment_ribbon',
        'web_sheet_full_width',
        # Infra modules
        'logging_json',
        'monitoring_status',
        'smile_redis_session_store',
        # OCA/Connector
        'base_import_async',
    ],
    'data': [
    ],
    'application': True,
    'post_init_hook': 'post_init',
}
