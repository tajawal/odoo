FROM tajawalcom/odoo:11.0
RUN mkdir -p /opt/finance_hub/src
RUN mv /tmp/odoo /opt/finance_hub/src/odoo
WORKDIR /opt/finance_hub
ADD . .
RUN /bin/bash -c "source /usr/local/bin/virtualenvwrapper.sh \
                  mkvirtualenv odoo-odoo_finance_hub -a . --python=$(which python3)"
RUN pip install --exists-action i --src src -r requirements.txt -e .
CMD sh /opt/finance_hub/infra/start.sh
