{
    "name": "Product Sync",
    "version": "1.0",
    "summary": "Sync products with external APIs",
    "category": "Inventory",
    "author": "Your Name",
    "depends": ["base", "product", "stock", "point_of_sale"],
    "installable": True,
    "application": False,
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'product_sync/static/src/js/kanban_controller.js',
            'product_sync/static/src/xml/kanban_controller.xml',
        ],
    },
}
