#!/usr/bin/env bash
cat > /opt/finance_hub/odoo.cfg << EOL
[options]
running_env=$myenv
admin_passwd=$admin_passwd
worker=$worker
server_wide_modules=web,queue_job,logging_json
limit_memory_hard = 1677721600
limit_memory_soft = 629145600
limit_request = 8192
limit_time_cpu = 1200
limit_time_real = 1500
max_cron_threads = 1
log_level=debug_rpc

# redis options
enable_redis = $enable_redis
redis_host = $redis_host
redis_port = $redis_port
redis_dbindex = $redis_dbindex
redis_pass =

[hub_backend.$myenv-hub]
hub_api_location=$hub_api_location
hub_api_username=$hub_api_username
hub_api_password=$hub_api_password
config_api_url=$config_api_url
config_api_username=$config_api_username
config_api_password=$config_api_password
oms_finance_api_url=http://finance-oms-api:5000/

[sap_backend.dev-sap]
sap_xml_api_url=http://finance-sap-xml-api:5000/

[sap_backend.live-sap]
sap_xml_api_url=http://finance-sap-xml-api:5000/

[sap_xml_api]
sap_xml_api_url=$sap_xml_api_url
sap_xml_api_username=$sap_xml_api_username
sap_xml_api_password=$sap_xml_api_password
hub_source=$hub_source

[ir.config_parameter]
ir_attachment.location=db

EOL

odoo -c /opt/finance_hub/odoo.cfg -d $DB_NAME -r $DB_USER -w $DB_PASSWORD --db_host $DB_HOST -u all --without-demo=WITHOUT_DEMO
