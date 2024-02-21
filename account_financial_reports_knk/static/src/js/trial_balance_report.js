odoo.define('account_financial_reports_knk.trial_balance_report', function(require) {
    'use strict';

    var core = require('web.core');
    var framework = require('web.framework');
    var stock_report_generic = require('stock.stock_report_generic');
    var { WarningDialog } = require("@web/legacy/js/_deprecated/crash_manager_warning_dialog");
    var session = require('web.session');
    var datepicker = require('web.datepicker');
    var field_utils = require('web.field_utils');
    var QWeb = core.qweb;
    var _t = core._t;
    var session = require('web.session');

    var TrialBalanceReport = stock_report_generic.extend({
        events: {},
        init: function(){
            this._super.apply(this, arguments);
            this.given_context.dates = 'this_month'
            this.given_context.entry_type = 'all'
            this.given_context.journal_id = '0'
            this.given_context.company_id = '0'
            this.given_context.prev_period = '0'
            this.given_context.last_period = '0'
            this.given_context.custom_date = false
        },
        get_html: function() {
            var self = this;
            var args = [
                this.given_context.dates,
                this.given_context.entry_type,
                this.given_context.journal_id,
                this.given_context.company_id,
                this.given_context.prev_period,
                this.given_context.last_period,
            ];
            return this._rpc({
                    model: 'report.account_financial_reports_knk.report_trial_balance',
                    method: 'get_html',
                    args: args,
                    context: this.given_context,
                })
                .then(function(result) {
                    self.data = result;
                    self.renderSearch()
                });
        },
        set_html: function() {
            var self = this;
            return this._super().then(function() {
                self.$('.o_content').html(self.data.lines);
                self.renderSearch();
                self.update_cp();
            });
        },
        render_html: function(event, $el, result) {
            if (result.indexOf('mrp.document') > 0) {
                if (this.$('.o_mrp_has_attachments').length === 0) {
                    var column = $('<th/>', {
                        class: 'o_mrp_has_attachments',
                        title: 'Files attached to the product Attachments',
                        text: 'Attachments',
                    });
                    this.$('table thead th:last-child').after(column);
                }
            }
            $el.after(result);
            $(event.currentTarget).toggleClass('o_account_report_foldable o_account_report_unfoldable fa-caret-right fa-caret-down');
            this._reload_report_type();
        },
        getControlPanelProps: function() {
            return { $buttons: this.$buttons, $searchview_buttons: this.$searchView}
        },
        update_cp: function() {
            var status = {
                cp_content: {
                    $buttons: this.$buttonPrint,
                    $searchview_buttons: this.$searchView
                },
            };
            return this.updateControlPanel(status);
        },
        renderSearch: function() {
            console.log(">>>>>>>>>>>")
            this.$buttons = $(QWeb.render("tb.button", {}));
            this.$buttons.find('.o_report_print_pdf').bind('click', this._onClickPrint.bind(this));
            this.$buttons.find('.o_report_print_xls').bind('click', this._onClickPrint_xls.bind(this));
            this.$searchView = $(QWeb.render('tb.report_tb_search', _.omit(this.data, 'lines')));
            this.$searchView.find('.o_tb_report_entry_type').on('change', this._onChangeEntryType.bind(this));
            this.$searchView.find('.o_tb_report_journals').on('change', this._onChangeJournals.bind(this));
            this.$searchView.find('.o_tb_report_companies').on('change', this._onChangeCompanies.bind(this));
            this.$searchView.find('.js_foldable_trigger').bind('click', this._onClickFoldable.bind(this));
            this.$searchView.find('.js_account_report_date_cmp_filter').bind('click', this._onDateCMP.bind(this));
            this.$searchView.find('.js_account_report_date_filter').bind('click', this._onChangeCustomDates.bind(this));
            var $datetimepickers = this.$searchView.find('.js_account_reports_datetimepicker');
            var options = { // Set the options for the datetimepickers
                locale : moment.locale(),
                format : 'L',
                icons: {
                    date: "fa fa-calendar",
                },
            };
            // attach datepicker
            $datetimepickers.each(function () {
                var name = $(this).find('input').attr('name');
                var defaultValue = $(this).data('default-value');
                $(this).datetimepicker(options);
                var dt = new datepicker.DateWidget(options);
                dt.replace($(this)).then(function () {
                    dt.$el.find('input').attr('name', name);
                    if (defaultValue) { // Set its default value if there is one
                        dt.setValue(moment(defaultValue));
                    }
                });
            });
        },
        _onChangeCustomDates: function(ev) {
            $(ev.currentTarget).closest('.o_filter_menu').find('.dropdown-item').removeClass('selected');
            var selectedOption = ev.currentTarget.attributes['data-filter'].value;
            ev.currentTarget.classList.add("selected");
            const selected_text = ev.currentTarget.text
            $(ev.currentTarget).closest('.o_dropdown').find('.selected_date').text(selected_text)
            this.given_context.dates = selectedOption;
            var error = false
            if (this.given_context.dates === 'custom') {
                var date_from = $(this.el).find('.o_datepicker_input[name="date_from"]')
                var date_to = $(this.el).find('.o_datepicker_input[name="date_to"]')
                if (date_from.length > 0){
                    error = date_from.val() === "" || date_to.val() === "";
                    this.given_context.from_date = field_utils.parse.date(date_from.val());
                    this.given_context.to_date = field_utils.parse.date(date_to.val());
                }
                else {
                    error = date_to.val() === "";
                    this.given_context.to_date = field_utils.parse.date(date_to.val());
                }
            }
            if (error) {
                new WarningDialog(this, {
                    title: _t("Odoo Warning"),
                }, {
                    message: _t("Date cannot be empty")
                }).open();
            } else {
                this._reload();
            }
        },
        _onChangeEntryType: function(ev) {
            var entry_type = $("option:selected", $(ev.currentTarget)).data('type');
            this.given_context.entry_type = entry_type;
            this._reload();
        },
        _onChangeJournals: function(ev) {
            var journal_id = $("option:selected", $(ev.currentTarget)).val();
            this.given_context.journal_id = journal_id;
            this._reload();
        },
        _onChangeCompanies: function(ev) {
            var company_id = $("option:selected", $(ev.currentTarget)).val();
            this.given_context.company_id = company_id;
            this._reload();
        },
        _onClickFoldable: function(ev) {
            $(ev.target).toggleClass('o_closed_menu o_open_menu');
            // this.$searchView.find('.o_foldable_menu[data-filter="' + $(ev.target).data('filter') + '"]').toggleClass('o_closed_menu');
            $(this.el).find('.o_foldable_menu[data-filter="' + $(ev.target).data('filter') + '"]').toggleClass('o_closed_menu');
        },
        _onDateCMP: function(ev) {
            var prev_period = $(this.el).find('.js_input_prev_period').val();
            var last_period = $(this.el).find('.js_input_last_period').val();
            this.given_context.prev_period = prev_period;
            this.given_context.last_period = last_period;
            this._reload();
        },
        _onClickPrint: function(ev) {
            framework.blockUI();
            var reportname = 'account_financial_reports_knk.report_trial_balance?docids=' + 1 +
                '&dates=' + this.given_context.dates +
                '&journal_id=' + this.given_context.journal_id +
                '&company_id=' + this.given_context.company_id +
                '&entry_type=' + this.given_context.entry_type +
                '&prev_period=' + this.given_context.prev_period +
                '&last_period=' + this.given_context.last_period;
            var action = {
                'type': 'ir.actions.report',
                'report_type': 'qweb-pdf',
                'report_name': reportname,
                'report_file': 'account_financial_reports_knk.report_trial_balance',
            };
            return this.do_action(action).then(function() {
                framework.unblockUI();
            });
        },
        _onClickPrint_xls: function(ev) {
            var self = this;
             return this._rpc({
                model: 'report.account_financial_reports_knk.report_trial_balance',
                method: 'account_move_print_xls_report',
                args: [{}],
                context: self.given_context,
            })
            .then(function (result) {
                session.get_file({
                    url: '/web/trial_balance_report/export',
                    data: { data: JSON.stringify(result)},
                    complete: framework.unblockUI,
                    error: (error) => self.call('crash_manager', 'rpc_error', error),
                });
            });
        },
        _reload: function() {
            var self = this;
            return this.get_html().then(function() {
                self.$('.o_content').html(self.data.lines);
                self._reload_report_type();
            });
        },
        _reload_report_type: function() {
            this.$('.o_mrp_bom_cost.o_hidden, .o_mrp_prod_cost.o_hidden').toggleClass('o_hidden');
            if (this.given_context.report_type === 'bom_structure') {
                this.$('.o_mrp_bom_cost, .o_mrp_prod_cost').toggleClass('o_hidden');
            }
        },
    });

    core.action_registry.add('trial_balance_report', TrialBalanceReport);
    return TrialBalanceReport;

});