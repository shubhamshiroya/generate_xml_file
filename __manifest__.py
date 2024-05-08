{
    'name': 'Generate XML File',
    'version': '14.0',
    'depends': ['sale', 'sale_management'],
    'author': 'shubham',
    'category': 'General',
    'sequence': -10,
    'description': """ Generate XML File for sale order""",
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'wizards/sale_order_wizard_view.xml',
        'wizards/xml_file_wizard_view.xml',
    ],

    'installable': True,
    'application': True,

}
