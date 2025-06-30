odoo.define('ing_seguro.auto_print_report', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var ActionManager = require('web.ActionManager');

    ActionManager.include({
        _executeReportAction: function (action, options) {
            if (action.report_type === 'qweb-pdf') {
                var self = this;
                var report_url = '/reports/' + action.report_name + '?doc_ids=' + action.context.active_ids.join(',');

                // Abrir PDF en nueva pestaña y enviar a imprimir
                var printWindow = window.open(report_url, '_blank');
                if (printWindow) {
                    printWindow.onload = function () {
                        printWindow.print();
                    };
                }

                return Promise.resolve();
            }
            return this._super(action, options);
        },
    });
});
