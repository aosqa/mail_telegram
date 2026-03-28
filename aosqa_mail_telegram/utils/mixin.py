import re
from odoo import models
import telegramify_markdown

class TelegramUtilsMixin(models.AbstractModel):
    _name = 'telegram.utils.mixin'
    _description = 'Telegram Utilities Mixin'


    def get_telegram_message(self,text):
        user = self.env.user
        username = user.partner_id.telegram_username or user.name
        company = user.company_id.name or ''
        return telegramify_markdown.markdownify(f"{text}\n\nThis message is sent by {username}({company})")
