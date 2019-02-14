# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "odoo_finance_hub",
    'description': """
        Odoo aplication for odoo_finance_hub""",
    'author': 'ACSONE SA/NV',
    'website': "http://acsone.eu",
    'category': 'odoo_finance_hub',
    'version': '11.0.1.4.4',
    'license': 'AGPL-3',
    'depends': [
        # odoo_finance_hub open source addons
        'ofh_base_currency',
        'ofh_payment_request_invoice',
        'ofh_payment_request_sap_s3_bucket',

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
    ],
    'data': [
    ],
    'application': True,
    'post_init_hook': 'post_init',
}
