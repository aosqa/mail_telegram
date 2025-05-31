# __manifest__.py
{
    'name': 'Telegram File Sender',
    'version': '1.0',
    'depends': ['base','mail','sale'],
    'external_dependencies': {
        'python': ['telegramify-markdown'],
    },
    'data': [
        'security/ir.model.access.csv',
        "wizard/telegram_composer_views.xml",
        "views/res_partner.xml",
        "views/telegram_bot_views.xml",
        "views/telegram_messages_history.xml",
        "data/ir_sequence_data.xml",
        
    ],
     'assets': {
         'web.assets_backend': [
         ]
     },
    'application': True,
}
