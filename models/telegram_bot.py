from odoo import models, fields, api,_
import requests
import logging

_logger = logging.getLogger(__name__)

class TelegramBot(models.Model):
    _inherit = 'telegram.utils.mixin'
    _name = 'telegram.bot'
    _description = 'Telegram Bot Message'
    _order = 'sequence asc'
    name = fields.Char(string="Name", required=True)
    message = fields.Text(string="Message")
    telegram_user_id = fields.Many2one('res.partner', string="Test Recipient",domain = "[('telegram_username','!=',False),('telegram_chat_id','!=',False)]",groups='base.group_system')
    bot_token = fields.Char(string="Bot Token",groups='base.group_system')
    sequence = fields.Integer(string="Sequence" , help="lower points fetched first")
    
    def action_test(self):
        """Test Telegram Bot by sending a sample message."""
        for record in self:
            send_status =  False
            if not record.bot_token:
                raise ValueError(_("Bot Token is required to send messages."))
            if not record.telegram_user_id or not record.telegram_user_id.telegram_chat_id:
                raise ValueError(_("Recipient must have a Telegram chat ID."))

            try:
                url = f'https://api.telegram.org/bot{record.bot_token}/sendMessage'

                full_message = self.get_telegram_message(record.message or " ")
                payload = {
                    'chat_id': record.telegram_user_id.telegram_chat_id,
                    'text': full_message,
                    'parse_mode': 'HTML',
                }

                response = requests.post(url, data=payload)
                if response.status_code == 200:
                    message = _("Test message sent successfully!")
                    send_status=True
                else:
                    message = _("Failed to send test message:\n%s") % response.json()['description']

            except Exception as e:
                _logger.exception("Telegram send error")
                message = _("Error sending test message:\n%s") % str(e)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Telegram Bot'),
                'message': message,
                'type': 'success' if send_status else 'danger',
                'sticky': False,
            }
        }
