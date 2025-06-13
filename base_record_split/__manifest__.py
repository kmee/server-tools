{
    "name": "Base Record Split",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "author": "KMEE, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/base_record_split_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
