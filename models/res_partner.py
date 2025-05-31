from odoo import models, api,fields
import re

class ResPartner(models.Model):
    _inherit = "res.partner"
    telegram_username = fields.Char(string="Telegram Username")
    telegram_chat_id = fields.Char(string="Telgram Chat ID")

    @api.depends('complete_name', 'email', 'vat', 'state_id', 'country_id', 'commercial_company_name')
    @api.depends_context('show_address', 'partner_show_db_id', 'address_inline', 'show_email', 'show_vat', 'lang','show_telegram_username','show_telegram_chat_id')
    def _compute_display_name(self):
        for partner in self:
            name = partner.with_context({'lang': self.env.lang})._get_complete_name()
            if partner._context.get('show_address'):
                name = name + "\n" + partner._display_address(without_company=True)
            name = re.sub(r'\s+\n', '\n', name)
            if partner._context.get('partner_show_db_id'):
                name = f"{name} ({partner.id})"
            if partner._context.get('show_telegram_username') and partner.telegram_username:
                 name = f"{name} ({partner.telegram_username})"
            if partner._context.get('show_telegram_chat_id') and partner.telegram_chat_id:
                 name = f"{name} ({partner.telegram_chat_id})"
            if partner._context.get('address_inline'):
                splitted_names = name.split("\n")
                name = ", ".join([n for n in splitted_names if n.strip()])
            if partner._context.get('show_email') and partner.email:
                name = f"{name} <{partner.email}>"
            if partner._context.get('show_vat') and partner.vat:
                name = f"{name} ‒ {partner.vat}"

            partner.display_name = name.strip()

        