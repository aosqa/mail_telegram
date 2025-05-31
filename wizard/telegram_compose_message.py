import base64
import requests
from odoo import _, api, fields, models
from odoo.exceptions import  ValidationError
import json
import uuid
from time import sleep



class TelegramComposer(models.TransientModel):
    _inherit = 'telegram.utils.mixin'
    _name = 'telegram.compose.message'
    body = fields.Text('Contents',help="Use Markdown ",compute=False, default='')
    
    attachment_ids = fields.Many2many(
        'ir.attachment', 'telegram_compose_message_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')
    partner_ids = fields.Many2many(
        'res.partner', 'telegram_compose_message_res_partner_rel',
        'wizard_id', 'partner_id', 'Receivers',
        context={
            "show_telegram_username":True,
            "show_telegram_chat_id":True
        },
        domain = "[('telegram_username','!=',False),('telegram_chat_id','!=',False)]",
        help="""Contacts That have Telgram username and chat ID
            - Remember: Those that doesn't have will not appear here"""
        )
    
    model = fields.Char('Related Document Model', index=True)
    res_id = fields.Integer('Related Document ID', index=True)
    record_name = fields.Char('Message Record Name', help="Name get of the related document.")
    template_id = fields.Many2one(
        'telegram.template', 'Use template',  domain="[('model', '=', model)]",
      )



    @api.onchange('template_id')
    def onchange_template_id(self):
        for record in self:
            if not record.template_id:
                return False
            report = record.template_id.report_template
            record.body=self.env['mail.render.mixin']._render_template(record.template_id.body_html, record.model, [record.res_id])[record.res_id]
            filename = self.env['mail.render.mixin']._render_template(record.template_id.report_name, record.model, [record.res_id])[record.res_id]
            model_obj = self.env[record.model].browse(record.res_id)
            report_result = report._render_qweb_pdf(report,model_obj.ids)
            pdf_content, _ = report_result
            attachment = self.env['ir.attachment'].create({
                    'name': filename,
                    'datas': base64.b64encode(pdf_content),
                    'res_model': record._name,
                    'res_id': record.id,
                    'type': 'binary',
                    'mimetype': 'application/pdf',
                })
            record.attachment_ids = [(4, attachment.id)]

    def _send_as_message(self, bot_token, chat_id):
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': self.get_telegram_message(self.body or " " ),
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
            full_message = self.get_telegram_message(record.body or " " )
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


    def send_message(self):
        bot = self.env['telegram.bot'].search([],limit=1)
        for record in self:
            for partner in record.partner_ids:
                tg_msg_hist = self.env['telegram.messages.history'].create({
                    'body': record.body,
                    'template_id': record.template_id.id,
                    'attachment_ids': [(6, 0, record.attachment_ids.ids)],
                    'partner_id': partner.id,  # if One2many is linked to Many2one on partner model
                    'model_id': self.env['ir.model']._get(record.model).id if record.model else False,
                    'model': record.model,
                    'res_id': record.res_id,
                    'record_name': record.record_name,
                   
            })
                chat_id = partner.telegram_chat_id
                if record.attachment_ids:
                    val=self._send_as_media_group(bot_token = bot.bot_token,chat_id=chat_id)
                else:
                    val=self._send_as_message(bot_token = bot.bot_token,chat_id=chat_id)
                tg_msg_hist.write(
                    val
                )

        return True
        
    
    