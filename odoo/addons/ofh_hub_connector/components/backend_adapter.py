# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import requests
from datetime import datetime
from odoo.exceptions import MissingError
from odoo.addons.component.core import AbstractComponent


class HubAPI:

    def __init__(
            self, url: str, username: str, password: str, token: str) -> None:
        self.url = url
        self.username = username
        self.password = password
        self.token = token
        self.headers = {
            'Content-type': 'application/json;charset=UTF-8',
            'user-agent': 'finance_hub_api/0.1',
            'Accept': 'application/json',
        }

    def getAuthToken(self) -> str:
        payload = {
            'email': self.email,
            'password': self.password,
        }
        url = '{}api/auth/token'.format(self.url)
        try:
            response = requests.post(
                url, params=payload, headers=self.headers, timeout=3)
            response.raise_for_status()
            data = response.json()
            if 'data' in data:
                return data['data'].get('token')
            return ""
        except requests.exceptions.BaseHTTPError as err:
            raise MissingError("Could not generate token")

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
        headers['Authorization'] = "Bearer {}".format(self.token)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError as err:
            raise MissingError("Could not generate token")

    # TODO: do we need only processed payment request?
    # TODO: a separated end point for the payment request?
    def getProcessedPaymentRequest(
            self, from_date: datetime, to_date: datetime) -> list:
        """
        Get processed Payment Request from HUB.
        Returns:
            list -- list of payment request dictionary details.
        """

        url = '{}api/sap/orders-list-raw'.format(self.url)
        headers = self.headers
        headers['Authorization'] = "Bearer {}".format(self.token)
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
            return response.json().get('payment_requests')
        except requests.exceptions.BaseHTTPError as err:
            raise MissingError("Could find payment requests")

    def get_payment_request_by_track_id(self, track_id) -> dict:
        url = '{}api/sap/payment-request-raw/{}'.format(
            self.url, track_id)
        headers = self.headers
        headers['Authorization'] = "Bearer {}".format(self.token)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError as err:
            raise MissingError("Could not get payment request details")

    def get_raw_order(self, order_id: str) -> dict:
        url = '{}api/sap/order-raw/{}'.format(self.url, order_id)
        headers = self.headers
        headers['Authorization'] = "Bearer {}".format(self.token)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.BaseHTTPError as err:
            raise MissingError("Could not get payment request details")


class HubAdapter(AbstractComponent):
    """[summary]."""

    _name = 'hub.adapter'
    _inherit = ['base.backend.adapter', 'base.hub.connector']
    _usage = 'backend.adapter'

    def search(self, filters: dict=None) -> list:
        """ Search records according to some criterias. """
        raise NotImplementedError

    def read(self, id, attributes=None):
        """ Returns the information of a record. """
        raise NotImplementedError
