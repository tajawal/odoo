=====================
Odoo Odoo_finance_hub
=====================

.. contents::

Development environment howto
=============================

Initialize virtualenv
---------------------

create and activate virtualenv, possibly with virtualenvwrapper's
``mkvirtualenv odoo-odoo_finance_hub -a . --python=$(which python3)``

To save some time copy Odoo 11.0 sources in src/odoo,
and do ``git clean -ffdx`` in src/odoo.

Install everything
------------------

.. code:: bash

   pip install --src src -r requirements.txt -e .

Only when there is a need to refresh the frozen dependencies,
review ``gitaggregate.yaml`` and ``requirements-dev.txt``, then
run:

.. code:: bash

   gitaggregate -c gitaggregate.yaml -p
   rmvirtualenv odoo-odoo_finance_hub
   mkvirtualenv odoo-odoo_finance_hub -a . --python=$(which python3)
   pip install --src src --pre -r requirements-dev.txt
   ./freeze.sh
   git commit requirements.txt

Run
---

   odoo -c odoo.cfg -d {db_name}

Update Module
-------------

   odoo -c odoo.cfg -d {db_name} -u {module_name}

Update All DB
-------------

   odoo -c odoo.cfg -d {db_name} -u all

Install New Module
------------------

   odoo -c odoo.cfg -d {db_name} -i {module_name}

Run Tests
---------

   odoo -c odoo.cfg -d {db_name} [-i {module_name}] --test-enable [--stop-after-init]

Release
-------

First make sure you have been testing using the correct dependencies by
running ``./freeze.sh`` and checking there is no change in ``requirements.txt``.

To release manually
...................

- update version in ``acsoo.cfg`` and ``odoo_finance_hub_all/__manifest__.py``
- commit everything
- run ``acsoo release``

At that point the resulting wheel files in ``./release`` contain all the
code to be deployed.
