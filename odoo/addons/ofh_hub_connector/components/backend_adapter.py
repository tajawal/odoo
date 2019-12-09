# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import requests
from datetime import datetime
from odoo.exceptions import MissingError
from odoo.addons.component.core import AbstractComponent


class HubAPI:

    def __init__(self, oms_finance_api_url: str):
        self.oms_finance_api_url = oms_finance_api_url
        self.headers = {
            'Content-type': 'application/json;charset=UTF-8',
            'user-agent': 'finance_hub_api/0.1',
            'Accept': 'application/json',
        }

    # Payment Request End points
    def get_list_payment_request(
            self, from_date: datetime, to_date: datetime) -> list:
        url = f"{self.oms_finance_api_url}payment_request/list"
        query = {
            'date_to': to_date.strftime('%Y-%m-%d %H:%M:%S'),
            'date_from': from_date.strftime('%Y-%m-%d %H:%M:%S'),
        }
        try:
            response = requests.get(url, headers=self.headers, params=query)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not get payment request list")

    # Get payment request details using oms-finance-api
    def get_payment_request_by_track_id(self, track_id) -> dict:
        url = '{}payment_request/detail/{}'.format(
            self.oms_finance_api_url, track_id)
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not get payment request details")

    # Get payment details using oms-finance-api
    def get_payment_by_track_id(self, track_id) -> dict:
        url = f"{self.oms_finance_api_url}payment/list/{track_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not get payment details")

    # Get payment details using oms-finance-api by Order Mongo Id
    def get_payment_by_order_id(self, order_id) -> dict:
        url = f"{self.oms_finance_api_url}payment/detail?id={order_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not get payment details")

    def get_raw_order(self, order_id: str) -> dict:
        # TODO: this is purely manual for test purpose only
        url = f"{self.oms_finance_api_url}sale_orders/detail?order_id={order_id}&type=initial"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not get sale order details.")

    def get_list_order(self, from_date: datetime, to_date: datetime) -> dict:
        # TODO: this is purely manual for test purpose only
        url = f"{self.oms_finance_api_url}sale_orders/list"
        query = {
            'date_to': to_date.strftime('%Y-%m-%d %H:%M:%S'),
            'date_from': from_date.strftime('%Y-%m-%d %H:%M:%S'),
        }
        try:
            response = requests.get(url, headers=self.headers, params=query)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError:
            raise MissingError("Could not get sale order list.")

    # Command Cryptic Endpoints
    def get_gds_daily_report(self, office_id: str, report_day: str) -> dict:
        """[summary]

        :param office_id: [description]
        :type office_id: str
        :param report_day: [description]
        :type report_day: str
        :raises MissingError: [description]
        :return: [description]
        :rtype: dict
        """
        if not office_id or not report_day:
            return {}
        url = f"{self.oms_finance_api_url}gds_reports/daily_report"
        payload = {
            'office': office_id,
            'report_day': report_day,
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json().get('data')
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not get payment request details")

    def gds_retrieve_pnr(self, office_id: str, locator: str) -> dict:
        """[summary]

        :param office_id: [description]
        :type office_id: str
        :param locator: [description]
        :type report_day: str
        :raises MissingError: [description]
        :return: [description]
        :rtype: dict
        """
        if not office_id or not locator:
            return {}
        url = f"{self.oms_finance_api_url}gds_reports/retrive_pnr"
        payload = {
            'office': office_id,
            'locator': locator,
        }
        try:
            response = requests.post(
                url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get('order_id')
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not get payment request details")


class HubAdapter(AbstractComponent):
    """[summary]."""

    _name = 'hub.adapter'
    _inherit = ['base.backend.adapter', 'base.hub.connector']
    _usage = 'backend.adapter'

    def search(self, filters: dict = None) -> list:
        """ Search records according to some criterias. """
        raise NotImplementedError

    def read(self, id, attributes=None):
        """ Returns the information of a record. """
        raise NotImplementedError
