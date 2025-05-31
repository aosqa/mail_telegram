
from bs4 import BeautifulSoup
from odoo.addons.mail.controllers.thread import ThreadController
from odoo import http
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.http import request


import re
from html import unescape

def strip_html_tags(html):
    """
    Strips HTML tags from the given text using BeautifulSoup.
    """
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()
    
    
class CustomThreadController(ThreadController):
    @staticmethod
    def strip_html_tags(html):
        """
        Strips HTML tags from the given text using BeautifulSoup.
        """
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()
    
   
    
    @http.route("/mail/message/post", methods=["POST"], type="json", auth="public")
    @add_guest_to_context
    def mail_message_post(self, thread_model, thread_id, post_data, context=None):
        message_data = super(CustomThreadController, self).mail_message_post(thread_model, thread_id, post_data, context)
        try:
            if post_data["partner_ids"]:
                composer = request.env['telegram.compose.message'].sudo().create({
                        'partner_ids':post_data["partner_ids"],
                        'attachment_ids':post_data["attachment_ids"],
                        "body":f"`{message_data['subject'] or 'on discuss'}`\n\n\n{self.strip_html_tags(message_data['body'])}",

                    })
                composer.sudo().send_message()
          
        except:
            pass
        
        return message_data

