import base64
import logging

import requests
import mimetypes
from odoo import _, api, fields, models
from time import sleep


class TelegramTemplate(models.Model):
    _inherit = ['mail.render.mixin', 'template.reset.mixin','telegram.utils.mixin']
    _name = 'telegram.template'
    _unrestricted_rendering = True

    name = fields.Char('Name', translate=True)
    model_id = fields.Many2one('ir.model', 'Applies to', help="The type of document this template can be used with")
    model = fields.Char('Related Document Model', related='model_id.model', index=True, store=True, readonly=True)
    body_html = fields.Text('Body', translate=True)
    report_name = fields.Char('Report Filename', translate=True,
                              help="Name to use for the generated report file (may contain placeholders)\n"
                                   "The extension can be omitted and will then come from the report type.")
    report_template = fields.Many2one('ir.actions.report', 'Optional report to print and attach')

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'telegram_template_attachment_rel',
        'telegram_template_id',
        'attachment_id',
        string='Telegram Attachments',
        help="Attach files to send with this Telegram message."
    )

    


    @api.model
    def default_get(self, fields):
        res = super(TelegramTemplate, self).default_get(fields)
        if res.get('model'):
            res['model_id'] = self.env['ir.model']._get(res.pop('model')).id
        return res
    
    def telegram_message(self):
        bot_token = '7769869014:AAETxD15XOoQzLw0kwsziQOZpaeRzqz3q2g'           # Replace with your bot token
        chat_id = '5569261806'
        url = f'https://api.telegram.org/bot{bot_token}/sendDocument'
        mime_type = 'application/octet-stream'
        for record in self:
            template_ctx = {
                    'model_description': record.model_id.display_name,
                    'company': self.env.company,
                    'record': record,
                }
            file_content=record.report_template._render_qweb_pdf([1])[0]
            data = {
                'chat_id': chat_id,
                'caption':record.name
            }
            files = {
                'document': ('hubo.pdf', file_content, mime_type),
            }
            sleep(1)
            response = requests.post(url, data=data, files=files)

            if response.status_code != 200:
                raise Exception(f'Telegram API Error: {response.status_code}\n{response.text}')
            
        return True
    

    def send_file_to_telegram(self,data=False):
        bot_token = '7769869014:AAETxD15XOoQzLw0kwsziQOZpaeRzqz3q2g'           # Replace with your bot token
        chat_id = '5569261806' 
        for record in self:
            if data:
                 mime_type = 'application/octet-stream'
                
            if not record.file_data or not record.file_name:
                continue

            file_content = base64.b64decode(record.file_data)
            mime_type, _ = mimetypes.guess_type(record.file_name)

            if not mime_type:
                mime_type = 'application/octet-stream'

            url = f'https://api.telegram.org/bot{bot_token}/sendDocument'
            data = {
                'chat_id': chat_id,
                'caption':record.name
            }
            files = {
                'document': (record.file_name, file_content, mime_type),
            }
            sleep(1)

            response = requests.post(url, data=data, files=files)

            if response.status_code != 200:
                raise Exception(f'Telegram API Error: {response.status_code}\n{response.text}')



