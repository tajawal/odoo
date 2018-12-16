#!/usr/bin/env bash
cat > /opt/finance_hub/odoo.cfg << EOL
[options]
running_env=$myenv
admin_passwd=$admin_passwd
worker=$worker
server_wide_modules=web,queue_job

[queue_job]
channels = root:$worker,root.hub:$worker,root.import:1

[hub_backend.$myenv-hub]
hub_api_location=$hub_api_location
hub_api_username=$hub_api_username
hub_api_password=$hub_api_password
config_api_url=$config_api_url
config_api_username=$config_api_username
config_api_password=$config_api_password


[sap_xml_api]
sap_xml_api_url=$sap_xml_api_url
sap_xml_api_username=$sap_xml_api_username
sap_xml_api_password=$sap_xml_api_password
hub_source=$hub_source

EOL

export PGPASSWORD=${db_password}
if psql -lqtA -h ${db_endpoint} --username ${db_user}| grep -q ${db_name}; then
  echo "exists"
  odoo -c ../odoo.cfg -d $db_name -r $db_user -w $db_password --db_host $db_endpoint -u all --without-demo=WITHOUT_DEMO
else
  echo "do not exist"
  odoo -c ../odoo.cfg -d $db_name -r $db_user -w $db_password --db_host $db_endpoint -i ofh_all --without-demo=WITHOUT_DEMO
fi

