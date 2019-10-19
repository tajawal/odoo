=====================
Odoo Odoo_finance_hub
=====================

.. contents::

Development environment howto
=============================

Install virtualenvwrapper
-------------------------

.. code:: bash
    pip3 install virtualenvwrapper

Then add the following lines to your ~/.bashrc:

.. code:: bash
export VIRTUALENVWRAPPER_PYTHON=$(which python3)
export VIRTUALENVWRAPPER_VIRTUALENV=$(dirname $VIRTUALENVWRAPPER_PYTHON)/virtualenv
source $(dirname $VIRTUALENVWRAPPER_PYTHON)/virtualenvwrapper.sh

Then

.. code:: bash
    source ~/.bashrc

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


Configuration
-------------

Run the following command and update the config file with the proper credentials and values

.. code:: bash

   cp odoo-example.cfg odoo.cfg

Run
---

.. code:: bash

   odoo -c odoo.cfg -d {db_name}

Update Module
-------------

.. code:: bash

   odoo -c odoo.cfg -d {db_name} -u {module_name}

Update All DB
-------------

.. code:: bash

   odoo -c odoo.cfg -d {db_name} -u all

Install New Module
------------------

.. code:: bash

   odoo -c odoo.cfg -d {db_name} -i {module_name}

Run Tests
---------

.. code:: bash

   odoo -c odoo.cfg -d {db_name} [-i {module_name}] --test-enable [--stop-after-init]

Release
-------

First make sure you have been testing using the correct dependencies by
running ``./freeze.sh`` and checking there is no change in ``requirements.txt``.

Install via Docker
------------------

Download the latest changes from `dev-machine <www.github.com/tajawal/dev-machine>`_ and run the following command:

.. code:: bash

    make finance-hub-up

And you will be able to access the application via http://finance-hub.tajawal.local:8080

To release manually
...................

- update ``bumpversion patch|minor|major``
- run ``acsoo release`` to tag the commit.

At that point the resulting wheel files in ``./release`` contain all the
code to be deployed.
