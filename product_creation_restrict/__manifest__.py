# -*- coding: utf-8 -*-

{
    'name': "Product Journal Creation Restriction",
    'summary': """Product Journal Creation Restriction""",
    'description': """Product Journal Creation Restriction.""",
    'author': "Ahmed Gaber",
    'license': 'LGPL-3',
    'category': 'account',
    'version': '13.0',
    'depends': ['account','product','point_of_sale'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    "images": [
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
