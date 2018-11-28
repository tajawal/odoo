# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from pymongo import MongoClient
from xml.etree import ElementTree as ET


class MongoDBConnection:
    """MongoDB Connection"""
    def __init__(self, host='localhost', port=27017):
        self.host = host
        self.port = port
        self.connection = None

    def __enter__(self):
        self.connection = MongoClient(self.host, self.port)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


class SapXmlApi:

    def __init__(self, db_name: str, host='localhost', port=27017):
        # TODO use the config files for db name and host
        self.db_name = db_name
        self.mongo_db = MongoDBConnection(host=host, port=port)

    def _get_sync_history_query(self, track_id: str) -> dict:
        """Return only sync history of refund order or refund doc that has
        been sent with sucess using the given `track_id`.

        Returns:
            dict -- {'concition1': 'value', ....}
        """
        return {
            'orderTrackId': track_id,
            'requestType': {'$in': ['refund_order', 'refund_doc']},
            'response': '200',
        }

    def get_sync_history_by_track_id(self, track_id: str) -> dict:
        with self.mongo_db as mongo:
            sync_collection = mongo.connection[self.db_name]['request_log']
            # TODO use _get_sync_history_query to get the right query
            # For now I'm suing the orderId not trackID
            sync_history = sync_collection.find(
                self._get_sync_history_query(track_id))
            if not sync_history:
                    return {}
            details = {}
            for record in sync_history:
                request_type = record.get('requestType')
                if not request_type:
                    continue
                payload = record.get('payload')
                if not payload:
                    continue
                if request_type == 'refund_order':
                    details[request_type] = self.get_refund_order_details(
                        payload=payload)
                else:
                    details[request_type] = self.get_refund_doc_details(
                        payload=payload)
            return details

    def get_refund_order_details(self, payload: str) -> dict:
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
        root = ET.fromstring(payload)
        details = {}
        # <soapenv:Envelope><soapenv:Body><doc:SalesOrder><Record><Header>
        for child in root[1][0][0][0]:
            details[child.tag] = child.text
        return details

    def get_refund_doc_details(self, payload: str) -> dict:
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

        root = ET.fromstring(payload)
        details = {}
        # <soapenv:Envelope><soapenv:Body><doc:DocumentPosting><Record>
        for child in root[1][0][0]:
            details[child.tag] = child.text
        return details
