{
    'name': 'Expenses Draft Entry',
    'version': '15.0',
    'license': 'LGPL-3',
    'author': 'Ahmed Gaber, ',
    'category': 'Expenses',
    'depends': [
        'base',
        'hr_expense',
        'purchase_request',
    ],
    "data": [
        "security/security.xml",
        "views/hr_expenses_views.xml",
    ],
    'installable': True,
}
