# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import requests
from odoo.addons.component.core import AbstractComponent


class SapXmlApi:

    def __init__(self, sap_xml_api_url: str):
        self.sap_xml_api_url = sap_xml_api_url
        self.headers = {
            'Content-type': 'application/json;charset=UTF-8',
            'user-agent': 'finance_hub_api/0.1',
            'Accept': 'application/json',
        }

    def send_sale_order(self, payload: dict) -> dict:
        url = f"{self.sap_xml_api_url}sale_order/send"
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response

    def visualize_sale_order(self, payload: dict) -> dict:
        url = f"{self.sap_xml_api_url}sale_order/visualize"
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response

    def send_payment(self, payload: dict) -> dict:
        url = f"{self.sap_xml_api_url}payment/send"
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response

    def visualize_payment(self, payload: dict) -> dict:
        url = f"{self.sap_xml_api_url}payment/visualize"
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response


class SapAdapter(AbstractComponent):
    """[summary]."""

    _name = 'sap.adapter'
    _inherit = ['base.backend.adapter', 'base.sap.connector']
    _usage = 'backend.adapter'

    def create(self, data, visualize=False):
        """ Create a record on the external system """
        raise NotImplementedError
