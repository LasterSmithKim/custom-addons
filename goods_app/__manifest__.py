{
    'name': 'Goods Management',
    'description': 'Manage goods logistics.',
    'author': 'SmithKim',
    'depends': ['base'],
    'application': True,

    'data':[
        'security/goods_security.xml',
        'security/ir.model.access.csv',
        'views/goods_menu.xml',
        'views/machine_view.xml'
    ]
}