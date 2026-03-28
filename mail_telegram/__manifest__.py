# __manifest__.py
{
    'name': 'Telegram Integration for Odoo',
    'summary': 'Send Odoo documents and notifications via Telegram',
    'description': """
Telegram Integration for Odoo
=============================

This module allows users to send Odoo reports such as Quotations, Invoices, and Payslips directly via Telegram.
It also enables real-time notifications for mentions and log notes using Telegram Bot API.

Key Features:
-------------
- Send Odoo QWeb reports as Telegram attachments
- Define Telegram message templates (similar to mail templates)
- Receive messages when mentioned in chatter
- Telegram composer wizard for previewing and sending
- Integration with partner Telegram usernames
    """,
    'version': "17.0.1.3.3",
    'category': 'Communication',
    'author': 'Abdulselam Molla',
    'website': 'https://github.com/aosqa/mail_telegram',  
    'depends': ['base', 'mail'],
    'external_dependencies': {
        'python': ['telegramify-markdown'],
    },
    'data': [
        'security/ir.model.access.csv',
        'wizard/telegram_composer_views.xml',
        'views/res_partner.xml',
        'views/telegram_bot_views.xml',
        'views/telegram_messages_history.xml',
        'data/ir_sequence_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
