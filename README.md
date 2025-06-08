# 💌 HTML Email Sender with Python

![SMTP Banner](https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif)

> Send stylish HTML emails 📧 with language support, customizable templates, and zero external libraries — just Python magic 🪄

---

## 📦 Requirements

* OS: Windows / macOS / Linux
* Python: **3.10+ recommended** (Works best with Python 3.11 or 3.12+)
* No additional packages needed 🎉

---

## 🐍 Install Python

1. Go to 👉 [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download Python **3.12** or newer
3. During installation, **check “Add Python to PATH”**
4. After installing, verify in terminal / CMD:

```bash
python --version
```

Expected output: `Python 3.12.x`

---

## 📁 Project Structure

```
your_project/
├── server.py               # Main script
├── config.ini              # SMTP & sender config
├── emails.txt              # Recipient emails
├── template/               # HTML templates
│   └── welcome.html
└── language/               # Language UI files
    ├── en.ini
    └── vi.ini
```

---

## 🔧 `config.ini` Example

```ini
[Language]
lang = en

[SMTP]
server = smtp.gmail.com
port = 587
username = your_email@gmail.com
password = your_app_password
display_name = Your Display Name 😎
```

> 🛡 Tip: Use **App Passwords** if you’re using Gmail. Never share your real password.

---

## 🌍 Language File: `language/en.ini`

```ini
[TRANSLATE]
choose_template = 📝 Choose HTML template to send:
enter_subject = 📌 Enter email subject:
template_not_found = ⚠️ No HTML templates found in ./template/
email_not_found = 📭 No recipient emails found.
choose_template_input = Enter the number of the HTML you want to use:
sending_start = 🚀 Starting to send email to {count} recipients...
success = ✅ Successfully sent to: {email}
failure = ❌ Failed to send to: {email} | Error: {error}
invalid_choice = Invalid choice. Please try again.
```

> 🌐 Want to support more languages? Just create another `.ini` in `language/`.

---

## 📧 `emails.txt` Format

```txt
user1@example.com, user2@example.com, user3@example.com
```

* Emails are separated by `,` or `, `
* No line breaks needed

---

## ✨ HTML Template Example

Inside `template/welcome.html`:

```html
<!DOCTYPE html>
<html>
  <body>
    <h2 style="color: #00bfff;">Hey there!</h2>
    <p>This email was auto-sent using Python 🚀</p>
  </body>
</html>
```

Use your own styles, text, emojis — whatever feels ✨ you.

---

## 🚀 How to Run

From the terminal / CMD:

```bash
python server.py
```

You'll be prompted to:

1. Choose an HTML template
2. Enter the subject
3. The script reads `emails.txt` and sends one by one
4. Success/failure logs shown live on screen

---

## 🛡 How to Avoid Spam Folder

| ❌ Avoid                           | ✅ Recommended                             |
| --------------------------------- | ----------------------------------------- |
| Image-heavy or low-quality HTML   | Clean HTML with minimal styles            |
| Shouty subjects (SALE!!!)         | Neutral subject lines (no all caps)       |
| Bulk emails (1 email, many BCCs)  | Send emails **one-by-one** (already done) |
| No sender display name            | Use meaningful display name               |
| Missing SPF/DKIM on custom domain | Use proper SMTP (e.g., Gmail or SendGrid) |

> 💡 Always test-send to yourself first!

---

## 🧙‍♀️ Bonus Tips

* 👀 Use Canva to design email → Export HTML
* 🧪 Use multiple `.html` templates for A/B testing
* 🌐 Easily add multi-language UI support (just edit `language/*.ini`)
* 💼 Use professional SMTP like Mailgun, Brevo, SendGrid for production

---

## ✨ Made by Nyanko

> Feel free to fork, remix, or vibe with it 🚀
> [GitHub](https://github.com/Nyakkon) • [☕ Buy me boba](https://fe.wibu.me//img/QR.png)

