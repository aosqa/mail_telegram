# 📬 mail\_telegram – Telegram Integration for Odoo

**`mail_telegram`** is an Odoo module that enables Telegram messaging capabilities inside your Odoo environment. With this module, users can send important documents such as quotations, invoices, payslips, and more to partners via Telegram, using customizable templates. Additionally, users can receive Telegram messages when they're mentioned in Odoo chatter or log notes.

---

## 🚀 Key Features

* ✅ **Send Reports via Telegram**: Invoices, Sale Orders, Payslips, etc.
* ✅ **Custom Telegram Templates**: Works just like Odoo's email templates (`mail.template`)
* ✅ **Supports PDF Reports**: Attach Odoo QWeb reports (e.g., sale orders) as PDFs
* ✅ **Mentions & Notifications**: Receive messages when you're mentioned in log notes or chat
* ✅ **Composer Wizard**: Similar to email composer – use template, preview message, send instantly

---

## 📦 Installation

1. Copy or clone the module into your Odoo `addons` directory:

   ```bash
   git clone https://github.com/aosqa/mail_telegram.git
   ```

2. Restart the Odoo server:

   ```bash
   ./odoo-bin -u mail_telegram
   ```

3. Activate developer mode and install the module via Odoo UI.
     - go to settings/Technical/TElegram   and create bots and test

---

## 🧠 How It Works

### ✅ 1. Define a Telegram Template
  ## COnfigure first your bot like in above (3)

Just like an email template, you can define a Telegram message template and link it to a report.
-and it uses MarkdownV2 parser

```xml
<odoo>
    <record id="telegram_template_sale_order" model="telegram.template">
        <field name="name">Send Sale Order via Telegram</field>
        <field name="model_id" ref="sale.model_sale_order"/>
        <field name="body_html">
             Hello,  
             Your quotation `{{object.name}}` is ready for review.
        </field>
        <field name="report_name">{{object.name}}.pdf</field>
        <field name="report_template" ref="sale.action_report_saleorder"/>
    </record>
</odoo>
```

### ✅ 2. Trigger the Template via Button

Create an action or button (e.g. in the Sale Order) that opens the composer with default values pre-filled:

```python
from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_send_telegram(self):
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.id,
            'default_partner_ids': [(6, 0, self.partner_id.ids)],
            'default_template_id': self.env.ref('mail_telegram.telegram_template_sale_order').id,
        }
        return {
            'type': 'ir.actions.act_window',
            'name': 'Compose Telegram Message',
            'res_model': 'telegram.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }
```

---

## 🧩 Developer Guide

* **Templates** are defined in `telegram.template`, similar to `mail.template`.
* **Composer Wizard**: `telegram.compose.message` handles preview, message generation, and sending.
* **Telegram API Integration** is done using Python’s `requests`.

---

## 🛠️ Configuration

To use this module, you must configure your Telegram bot:

1. Create a bot via [BotFather](https://t.me/botfather)
2. Store the bot token in system parameters:

   * `telegram.bot_token`: Your bot's token
3. and in contacts (res.partner) There is a field telegram_username and telegram_chatid  this has to be filled both

---

## 📨 Mentions in Chatter

When users are mentioned in log notes or messages, they'll receive a direct message via Telegram (if their `telegram_username` and `telegram_chat_id` is set on their partner profile).

---

## 👤 Requirements

* Odoo 17 (Tested)
* Python libraries:

  * `telegramify-markdown`

You can install dependencies with:

```bash
pip install telegramify-markdown
```

---



## 🤝 Contributing

Pull requests are welcome! If you find bugs or have feature suggestions, feel free to open an issue.

---



---

## 👨‍💻 Author

**Abdulselam Molla** 

---

