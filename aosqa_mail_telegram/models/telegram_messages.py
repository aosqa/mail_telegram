import base64
import requests
from odoo import _, api, fields, models, tools, Command
from odoo.exceptions import ValidationError
import json
import uuid
from time import sleep


class TelegramUnsentMessages(models.Model):
    _inherit = 'telegram.utils.mixin'
    _name = 'telegram.messages.history'
    name = fields.Char(
        string="Order Reference",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))
    
    body = fields.Text('Contents',help="Use Markdown ",compute=False, default='')
    template_id = fields.Many2one(
        'telegram.template', 'Use template', index=True,
      )
    attachment_ids = fields.Many2many(
        'ir.attachment', 'telegram__message_history_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')
    partner_id = fields.Many2one(
        'res.partner', 'Receiver',
        context={
            "show_telegram_username":True,
            "show_telegram_chat_id":True
        },
        domain = "[('telegram_username','!=',False),('telegram_chat_id','!=',False)]",
        help="""Contacts That have Telgram username and chat ID
            - Remember: Those that doesn't have will not appear here"""
        )
    model_id = fields.Many2one('ir.model', 'Applies to', help="The type of document this template can be used with")
    model = fields.Char('Related Document Model', index=True)
    res_id = fields.Integer('Related Document ID', index=True)
    record_name = fields.Char('Message Record Name', help="Name get of the related document.")
    reason = fields.Char(string="reason")
    state = fields.Selection([('sent','Sent'),('unsent' , "unsent")])

    def _send_as_media_group(self, bot_token, chat_id):
        url = f'https://api.telegram.org/bot{bot_token}/sendMediaGroup'
        for record in self:
            media = []
            files = {}
            for attachment in record.attachment_ids:
                file_name = f"{uuid.uuid4()}_{attachment.name}"
                attach_name = f"attach://{file_name}"
                media.append({
                    'type': 'document',
                    'media': attach_name,
                    'caption': '',  # Add captions if needed
                })

                files[file_name] = (
                    attachment.name,
                    base64.b64decode(attachment.datas),
                    attachment.mimetype or 'application/octet-stream',
                )
            full_message = self.get_telegram_message(record.body or " ")
            media[-1]['caption'] = full_message
            media[-1]["parse_mode"] ="MarkdownV2"
            if not media:
                raise ValidationError("No valid documents to send.")
                
            data = {
                'chat_id': chat_id,
                'media': json.dumps(media),
            }
            sleep(1)
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                return {
                    "state":"sent",
                    "reason":" "
                }
            else:
               return  {
                "state":"unsent",
                "reason":response.json()["description"]
                }
            
        return {
            "state":"unsent",
            "reason":"Server Error"

        }
    def _send_as_message(self, bot_token, chat_id):
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        full_message = self.get_telegram_message(self.body or " ")
        payload = {
            'chat_id': chat_id,
            'text':full_message,
            'parse_mode':"MarkdownV2"
        }
        sleep(1)
        response = requests.post(url, data=payload)
        if response.status_code == 200:
                return {
                    "state":"sent",
                    "reason":" "
                }
        else:
               return  {
                "state":"unsent",
                "reason":response.json()["description"]
                }


    def resend_messages(self):
        bot = self.env['telegram.bot'].search([],limit=1)
        for record in self:
            chat_id = record.partner_id.telegram_chat_id
            if record.attachment_ids:
                val=self._send_as_media_group(bot_token = bot.bot_token,chat_id=chat_id)
            else:
                val=self._send_as_message(bot_token = bot.bot_token,chat_id=chat_id)
            record.write(
                val
            )
        return {'type': 'ir.actions.act_window_close'}
    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['create_date'])
                ) if 'create_date' in vals else None
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'telegram.message.history', sequence_date=seq_date) or _("New")

        return super().create(vals_list)

    
        




    