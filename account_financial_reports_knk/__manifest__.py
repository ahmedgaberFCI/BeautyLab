# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>)

{
    'name': 'Account Financial Reports For Community (Accounting Reports)',
    'version': '16.0.1.3',
    'summary': 'This module allows to create Financial Reports(General ledger, Trial Balance, Profit and loss, Balance Sheet) For Community. User can use different filters and print general ledger, trial balance, profit and loss and balance sheet.',
    'description': """This Module Allows To create Financial Reports Base on Configuration.
    """,
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://kanakinfosystems.com',
    'images': ['static/description/banner.jpg'],
    'depends': ['account', 'mrp', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/menus.xml',
        'report/report_views_main.xml',
        'report/report_profit_loss.xml',
        'report/report_balanace_sheet.xml',
        'report/report_general_ledger.xml',
        'wizard/output.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_financial_reports_knk/static/src/js/trial_balance_report.js',
            'account_financial_reports_knk/static/src/js/profit_loss_report.js',
            'account_financial_reports_knk/static/src/js/balanace_sheet_report.js',
            'account_financial_reports_knk/static/src/js/general_ledger_report.js',
            'account_financial_reports_knk/static/src/xml/account_financial_reports_knk.xml',
        ],
        'web.assets_common': [
            'account_financial_reports_knk/static/src/scss/account_report.scss',
        ],
        'web.report_assets_common': [
            'account_financial_reports_knk/static/src/scss/account_report.scss',
        ],
    },
    'installable': True,
    'price': 100,
    'currency': 'USD',
}
