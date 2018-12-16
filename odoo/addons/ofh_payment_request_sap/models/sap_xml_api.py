# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from xml.etree import ElementTree as ET

import requests
from odoo.exceptions import MissingError


class SapXmlApi:

    def __init__(
            self, sap_xml_url: str, sap_xml_username: str,
            sap_xml_password: str):

        self.sap_xml_url = sap_xml_url
        self.sap_xml_username = sap_xml_username
        self.sap_xml_password = sap_xml_password
        self._sap_xml_token = ''
        self.headers = {
            'Content-type': 'application/json;charset=UTF-8',
            'user-agent': 'finance_sap_xml_api/0.1',
            'Accept': 'application/json',
        }

    @property
    def _get_sap_xml_token(self) -> str:
        if self._sap_xml_token:
            return self._sap_xml_token
        payload = {
            'email': self.sap_xml_username,
            'password': self.sap_xml_password,
        }
        url = '{}api/sap/token'.format(self.sap_xml_url)
        try:
            response = requests.post(
                url, params=payload, headers=self.headers, timeout=3)
            response.raise_for_status()
            data = response.json()
            return data.get('token')
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not generate token")

    def sent_payment_request(self, payload: dict) -> dict:
        """Send sale_order/refund_order and sale_doc/refund_doc to SAP.

        Arguments:
            payload {dict} -- dict containing the payment request reference
            and the update values to use when sending the document to SAP.

        Returns:
            dict -- Request response.
        """
        if not payload:
            return {}

        url = '{}api/sap/send-request-xml'.format(self.sap_xml_url)
        headers = self.headers
        headers['Authorization'] = self._get_sap_xml_token
        try:
            response = requests.post(
                url, params=payload, headers=headers, timeout=3)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not generate token")
        if not data.get('data'):
            return {}
        xml_data = data.get('data')
        if payload.get('requestType') in ('sale_order', 'refund_order'):
            return self._get_details_from_order_xml(xml_data)
        elif payload.get('requestType') in ('sale_doc', 'refund_doc'):
            return self._get_details_from_payment_xml(xml_data)

    def get_refund_order_details(self, payload: dict) -> dict:
        """Process the refund sale payload xml and return details
        Arguments:
            payload {str} --
            <soapenv:Envelope>
            <soapenv:Header></soapenv:Header>
            <soapenv:Body>
            <sal:SalesOrder>
                <Record>
                    <Header>
                        <SystemID>ONLINE</SystemID>
                        <SalesType>ZRE</SalesType>
                        <CollectionMode>2</CollectionMode>
                        <BookingEntity>2003</BookingEntity>
                        <BookingNumber>A8073000835_6730946R0</BookingNumber>
                        <SalesOffice>TUS1</SalesOffice>
                        <Channel>20</Channel>
                        <Customer>7001614</Customer>
                        <FileID>abc106ec6730946R0</FileID>
                        <BookingDate>20180730</BookingDate>
                        <FEIndicator>ONL</FEIndicator>
                        <InvoiceCurrency>SAR</InvoiceCurrency>
                        <TaproInvoiceNumber>A8073000835</TaproInvoiceNumber>
                    </Header>
                    ...
                <Record>
            </sal:SalesOrder>
            </soapenv:Body>
            </soapenv:Envelope>
        Returns:
            dict -- {
                'SystemID': 'ONLINE',
                'SalesType': 'ZRE',
                'BookingNumber': 'A8073000835_6730946R0',
                ...
                'Assignment': 'abc106ec6730946R0',
            }
        """
        if not payload:
            return {}
        url = '{}api/sap/get-sent-request-status'.format(self.sap_xml_url)
        headers = self.headers
        headers['Authorization'] = self._get_sap_xml_token
        try:
            response = requests.post(
                url, params=payload, headers=headers, timeout=3)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not generate token")
        if not data.get('data'):
            return {}
        payload = data.get('data')[0].get('payload')
        return self._get_details_from_order_xml(payload)

    def _get_details_from_order_xml(self, payload: dict) -> dict:
        if not payload:
            return {}
        root = ET.fromstring(payload)
        details = {}
        # <soapenv:Envelope><soapenv:Body><doc:SalesOrder><Record><Header>
        for child in root[1][0][0][0]:
            details[child.tag] = child.text
        return details

    def get_refund_doc_details(self, payload: dict) -> dict:
        """ Process the refund payment payload xml and return details
        Arguments:
            payload {str} --
            <soapenv:Envelope>
            <soapenv:Header></soapenv:Header>
            <soapenv:Body>
            <doc:DocumentPosting>
                <Record>
                    <System>ONLINE</System>
                    <Transaction>PV_CARD</Transaction>
                    <CompanyCode>2003</CompanyCode>
                    <DocumentDate>20180730</DocumentDate>
                    <HeaderText>A8073000835_6730946R0</HeaderText>
                    <Reference>4242</Reference>
                    <Currency>SAR</Currency>
                    <Account1>7001614</Account1>
                    <Account2></Account2>
                    <Amount1>1532.00</Amount1>
                    <Amount2>-1496.76</Amount2>
                    <BankCharge>-35.24</BankCharge>
                    <SPLGL></SPLGL>
                    <SalesOffice>TUS1</SalesOffice>
                    <Material>10</Material>
                    <ReferenceKey1>800837</ReferenceKey1>
                    <ReferenceKey2>9W-</ReferenceKey2>
                    <ReferenceKey3></ReferenceKey3>
                    <Assignment>abc106ec6730946R0</Assignment>
                    <LineItemText>ahmed test</LineItemText>
                </Record>
            </doc:DocumentPosting>
            </soapenv:Body>
            </soapenv:Envelope>
        Returns:
            dict -- {
                'System': 'ONLINE',
                'Transaction': 'PV_CARD',
                ...
                'Assignment': 'abc106ec6730946R0',
            }
        """
        if not payload:
            return {}
        url = '{}api/sap/get-sent-request-status'.format(self.sap_xml_url)
        headers = self.headers
        headers['Authorization'] = "{}".format(
            self._get_sap_xml_token)
        try:
            response = requests.post(
                url, params=payload, headers=headers, timeout=3)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.BaseHTTPError:
            raise MissingError("Could not generate token")
        if not data.get('data'):
            return {}
        payload = data.get('data')[0].get('payload')
        self._get_details_from_payment_xml(payload)

    def _get_details_from_payment_xml(self, payload: dict) -> dict:
        if not payload:
            return {}
        root = ET.fromstring(payload)
        details = {}
        # <soapenv:Envelope><soapenv:Body><doc:SalesOrder><Record><Header>
        for child in root[1][0][0][0]:
            details[child.tag] = child.text
        return details
