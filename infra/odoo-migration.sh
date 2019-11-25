#!/usr/bin/env bash

odoo -c /opt/finance_hub/odoo.cfg -d $db_name -r $db_user -w $db_password --db_host $db_endpoint -u all --without-demo=WITHOUT_DEMO --stop-after-init

