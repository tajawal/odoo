Changes
-------

1.5.2 (2019-03-26)
------------------
* Manual OUTPUT VAT amount.

1.5.1 (2019-03-25)
------------------
* Empty GDSCode for change fee lineitem
* Change fee material for live sap.

1.5.0 (2019-03-13)
------------------
* VAT on change fee.
* Fix Payment Transaction calculation.

1.4.5 (2019-02-24)
------------------
* AYESHA-41: Use update_at date when sending to SAP.

1.4.4 (2019-02-14)
------------------
* GDS lines with zero amount should not be sent to SAP

1.4.3 (2019-02-14)
------------------
* AYES-38: Compute tax code using output vat

1.4.2 (2019-02-11)
------------------
* Allow users to import exchange rates.

1.4.1 (2019-02-10)
------------------
* Fix SAP Sale payload and zvt1 proration.

1.4.0 (2019-02-05)
-----------------
* AYESHA-18: Automatically download SAP Sale report from S3 bucket.
* AYESHA-75: Payment Request reconciliation and matching optimisation.
* AYESHA-79: Send payment request line wise when is possible.
* AYESHA-47: For Egypt payment request ZVD1 is equal to ZSEL.
* AYESHA-63: Add Transaction type to payment when sending to SAP.


1.3.6 (2019-01-23)
------------------
* [REF]ofh_payment_request_sap: Send the currency when sending payment to SAP.
