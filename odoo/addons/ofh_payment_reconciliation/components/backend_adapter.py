# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import requests
import json

try:
    from odoo.addons.server_environment import serv_config
except ImportError:
    logging.getLogger('odoo.module').warning(
        'server_environment not available in addons path.')


class SapXmlApi:

    def __init__(self):
        sap_xml_api_url = serv_config.get('sap_backend.live-sap', 'sap_xml_api_url')
        self.sap_xml_api_url = sap_xml_api_url
        self.headers = {
            'Content-type': 'application/json;charset=UTF-8',
            'user-agent': 'finance_hub_api/0.1',
            'Accept': 'application/json',
        }

    def generate_loader(self, payload: dict) -> dict:
        url = f"{self.sap_xml_api_url}payment_loader/generate"
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
