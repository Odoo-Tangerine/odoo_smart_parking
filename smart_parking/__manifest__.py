# -*- coding: utf-8 -*-
{
    'name': 'Smart Parking',
    'summary': """The addon integrates ViettelPost's API for delivery in Odoo.""",
    'description': """
        The Delivery ViettelPost addon is an Odoo integration that connects seamlessly to ViettelPost's API, 
        enabling efficient domestic and international package delivery and courier management. It streamlines 
        shipping logistics, tracking, and improves overall delivery processes within the Odoo ERP system for a 
        smooth customer experience.
    """,
    'author': "Long Duong Nhat",
    'category': 'External/Tangerine Project',
    'version': '17.0.1.0',
    'depends': ['mail', 'contacts', 'purchase', 'sale', 'l10n_vn'],
    'data': [
        'security/ir.model.access.csv',
        'data/spp_api_config.xml',
        'data/ir_cron.xml',
        'data/ir_config_parameter.xml',
        'views/spp_province_views.xml',
        'views/spp_district_views.xml',
        'views/spp_ward_views.xml',
        'views/spp_api_config_views.xml',
        'views/spp_sale_order_views.xml',
        'views/spp_product_views.xml',
        'views/spp_registered_vehicle_views.xml',
        'views/spp_user_face_views.xml',
        'views/spp_vehicle_io_history_views.xml',
        'views/spp_question_answer_views.xml',
        'views/menus.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True
}