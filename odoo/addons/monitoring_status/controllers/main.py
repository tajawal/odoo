# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import json

import werkzeug

from odoo import http
from odoo.addons.web.controllers.main import ensure_db


class Monitoring(http.Controller):

    @http.route('/monitoring/status', type='http', auth='none')
    def status(self):
        ensure_db()
        # TODO: add 'sub-systems' status and infos:
        # queue job, cron, database, ...
        headers = {'Content-Type': 'application/json'}
        info = {'status': 1}
        session = http.request.session
        # TODO: when session redis is set-up
        # We set a custom expiration of 1 second for this request, as we do a
        # lot of health checks, we don't want those anonymous sessions to be
        # kept. Beware, it works only when session_redis is used.
        # Alternatively, we could set 'session.should_save = False', which is
        # tested in odoo source code, but we wouldn't check the health of
        # Redis.
        if not session.uid:
            # in werkzeug `should_save` is property attribute that depends on
            # `modified` attribute. So it can't be set directly instead we
            # set the `modified` attribute to false when odoo checks
            # `should_save` it wll be False hence the session won't be stored.
            session.modified = False
        return werkzeug.wrappers.Response(json.dumps(info), headers=headers)
