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

[queue_job]
channels = root:4,root.hub:4:throttle=2,root.sap:4:throttle=2,root.import:1,root.import.gds:1,root.import.tf:1,root.import.sap:1,root.import.tv:1
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

export PGPASSWORD=${db_password}
if psql -lqtA -h ${db_endpoint} --username ${db_user}| grep -q ${db_name}; then
  echo "exists"
  echo "Remove ir_attachement from DB (Hack should be removed)"
  psql -h ${db_endpoint} --username ${db_user} -d ${db_name} -c "DELETE FROM ir_attachment WHERE url LIKE '/web/content/%';"
  odoo -c /opt/finance_hub/odoo.cfg -d $db_name -r $db_user -w $db_password --db_host $db_endpoint -u all --without-demo=WITHOUT_DEMO
  psql -h ${db_endpoint} --username ${db_user} -d ${db_name} -c "UPDATE queue_job SET state = 'pending' WHERE state IN ('enqueued', 'started');"
else
  echo "do not exist"
  odoo -c /opt/finance_hub/odoo.cfg -d $db_name -r $db_user -w $db_password --db_host $db_endpoint -i ofh_all --without-demo=WITHOUT_DEMO
fi

