from configparser import ConfigParser
from setuptools import setup


cfg = ConfigParser()
cfg.read('acsoo.cfg')


setup(
    version=cfg.get('acsoo', 'series') + '.' + cfg.get('acsoo', 'version'),
    name='odoo-addons-odoo-finance-hub',
    description='Odoo_finance_hub Odoo Addons',
    setup_requires=['setuptools-odoo'],
    install_requires=[
        'click-odoo-contrib',
        'python-json-logger',
        'boto3',
    ],
    odoo_addons={
        'depends_override': {
        },
        'external_dependencies_override': {
            'python': {
                'pythonjsonlogger': 'python-json-logger>=0.1.10',
            },
        },
    },
)
