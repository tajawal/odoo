# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import requests
from datetime import datetime
from odoo.exceptions import MissingError
from odoo.addons.component.core import AbstractComponent


class HubAPI:

    def __init__(
            self, hub_url: str, hub_username: str, hub_password: str,
            config_url: str, config_username: str, config_password: str, oms_finance_api_url: str):
        self.hub_url = hub_url
        self.oms_finance_api_url = oms_finance_api_url
        self.hub_username = hub_username
        self.hub_password = hub_password
        self.config_url = config_url
        self.config_username = config_username
        self.config_password = config_password
        self._hub_token = ''
        self._config_token = ''
        self.headers = {
            'Content-type': 'application/json;charset=UTF-8',
            'user-agent': 'finance_hub_api/0.1',
            'Accept': 'application/json',
        }

    @property
    def _get_hub_token(self) -> str:
        if self._hub_token:
            return self._hub_token
        payload = {
            'email': self.hub_username,
            'password': self.hub_password,
        }
        url = '{}api/auth/token'.format(self.hub_url)
        try:
            response = requests.post(
                url, params=payload, headers=self.headers, timeout=3)
            response.raise_for_status()
            data = response.json()
            if 'data' in data:
                self._hub_token = data['data'].get('token')
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not generate token")
        return self._hub_token

    @property
    def _get_config_token(self) -> str:
        if self._config_token:
            return self._hub_token
        payload = {
            "username": self.config_username,
            "password": self.config_password,
        }
        url = '{}token'.format(self.config_url)
        try:
            response = requests.post(
                url, params=payload, headers=self.headers, timeout=3)
            response.raise_for_status()
            data = response.json()
            self._config_token = data.get('token')
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not generate token")
        return self._config_token

    def getOrderChargeHistory(self, track_id: str) -> dict:
        """
        Get charge details using the track ID.
        Arguments:
            tack_id {str} -- Track ID of the order or the payment request

        Returns:
            dict -- Return dictionary containing the Charge details data.
        """
        url = '{}api/sap/charge-list-raw/{}'.format(self.url, track_id)
        headers = self.headers
        headers['Authorization'] = "Bearer {}".format(self._get_hub_token)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not generate token")

    def getProcessedPaymentRequest(
            self, from_date: datetime, to_date: datetime) -> list:
        """
        Get processed Payment Request from HUB.
        Returns:
            list -- list of payment request dictionary details.
        """

        url = '{}api/sap/processed-payment-requests'.format(self.hub_url)
        headers = self.headers
        headers['Authorization'] = "Bearer {}".format(self._get_hub_token)
        if not from_date:
            raise MissingError('You have to provide from_date')
        if not to_date:
            to_date = datetime.now()
        query = {
            'from': from_date.strftime('%Y-%m-%d %H:%M:%S'),
            'to': to_date.strftime('%Y-%m-%d %H:%M:%S'),
        }
        try:
            response = requests.get(url, headers=headers, params=query)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could find payment requests")

    def get_payment_request_by_track_id(self, track_id) -> dict:
        url = '{}api/sap/payment-request-raw/{}'.format(
            self.hub_url, track_id)
        headers = self.headers
        headers['Authorization'] = "Bearer {}".format(self._get_hub_token)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not get payment request details")

    # Get payment request details using oms-finance-api
    def get_payment_request_by_track_id_ofa(self, track_id) -> dict:
        url = '{}payment_request/detail/{}'.format(
            self.oms_finance_api_url, track_id)
        headers = {
            'cache-control': "no-cache",
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not get payment request details")

    def get_raw_order(self, order_id: str) -> dict:
        # TODO: this is purely manual for test purpose only
        url = f"http://localhost:5000/sale_orders/detail/{order_id}"
        headers = {
            'cache-control': "no-cache",
        }
        # url = '{}api/sap/order-raw/{}'.format(self.hub_url, order_id)
        # headers = self.headers
        # headers['Authorization'] = "Bearer {}".format(self._get_hub_token)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not get payment request details")

    def get_list_order(self, from_date: datetime, to_date: datetime) -> dict:
        # TODO: this is purely manual for test purpose only
        url = "http://localhost:5000/sale_orders/list"
        headers = {
            'cache-control': "no-cache",
        }
        query = {
            'date_to': to_date.strftime('%Y-%m-%d %H:%M:%S'),
            'date_from': from_date.strftime('%Y-%m-%d %H:%M:%S'),
        }
        try:
            response = requests.get(url, headers=headers, params=query)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError:
            raise MissingError("Could find payment requests")

    def get_raw_store(self, store_id: int) -> dict:
        url = '{}store/{}'.format(self.config_url, store_id)
        headers = self.headers
        headers['Authorization'] = "Bearer {}".format(self._get_config_token)
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not get sotre details")

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

        url = "http://localhost:5000/gds_reports/daily_report"
        headers = {
            'cache-control': "no-cache",
            'Content-Type': "application/json",
        }
        payload = {
            'office': office_id,
            'report_day': report_day,
        }
        try:
            response = requests.post(
                url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get('data')
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
