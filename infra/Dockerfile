FROM tajawalcom/odoo:11.0-1

RUN mkdir -p /opt/finance_hub/src && mv /tmp/odoo /opt/finance_hub/src/odoo

WORKDIR /opt/finance_hub
RUN /bin/bash -c "source /usr/local/bin/virtualenvwrapper.sh \
                  mkvirtualenv odoo-odoo_finance_hub -a . --python=$(which python3)"

ADD requirements.txt .
RUN pip install --exists-action i --src src -r requirements.txt

ADD . .

RUN pip install -e .
CMD sh /opt/finance_hub/infra/start.sh
