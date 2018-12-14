odoo.define('ofh_mail_activity.activity_menu', function (require) {
    "use strict";

    var systray = require('mail.systray');
    var session = require('web.session');

    systray.ActivityMenu.include({
        /**
         * Redirect to particular model view
         * @private
         * @param {MouseEvent} event
         */
        _onActivityFilterClick: function (event) {
            // fetch the data from the button otherwise fetch the ones from the parent (.o_mail_channel_preview).
            var data = _.extend({}, $(event.currentTarget).data(), $(event.target).data());
            console.log(data);
            var context = {};
            if (data.filter === 'my') {
                context['search_default_activities_overdue'] = 1;
                context['search_default_activities_today'] = 1;
            } else {
                context['search_default_activities_' + data.filter] = 1;
            }
            console.log(context);
            this.do_action({
                type: 'ir.actions.act_window',
                name: data.model_name,
                res_model:  data.res_model,
                views: [[false, 'list'], [false, 'form']],
                search_view_id: [false],
                domain: ['|', ['activity_user_ids', 'in', [session.uid]],
                         ['activity_user_id', '=', session.uid]],
                context:context,
            });
        },
    })
})