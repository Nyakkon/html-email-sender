# 💌 HTML Email Sender — MailDesk Web Edition

![SMTP Banner](https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif)

> Send stylish HTML emails via a modern Web UI or CLI interface.  
> Supports HTML templates, proxy configuration, multi-language UI, and works with pure Python — no external mail services required.

---

## 📦 Requirements

- OS: Windows / macOS / Linux
- Python: **3.11+ recommended**
- Flask (for Web UI only — installed automatically by setup script)

---

## 🚀 How to Run (Web UI)

### 🔹 Option 1: Auto setup (Windows only)

```bat
.\setup-enviroment.bat
````

This will:

* Create a virtual environment
* Install Flask
* Launch the web interface

Then open:
👉 `http://127.0.0.1:5000`

---

### 🔹 Option 2: Manual setup (cross-platform)

```bash
# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Flask
pip install flask

# Run the web interface
python maildesk_web.py
```

---

## 🖥️ What the Web UI Can Do

* Input SMTP + Proxy + Language settings
* Choose `.html` templates visually
* Edit subject and preview HTML
* Send to multiple recipients (one by one)
* Real-time success/failure logging
* Works in any modern browser

---

## ⚙️ Configuration (`config.ini`)

```ini
[Language]
lang = en

[SMTP]
server = smtp.gmail.com
port = 587
username = your_email@gmail.com
password = your_app_password
display_name = Your Name

[PROXY]
enabled = false
type = socks5
host = 127.0.0.1
port = 9050
```

> 🛡️ Tip: Use **App Passwords** for Gmail. Never share your real password.

---

## 🌍 Language Files

Example: `language/en.ini`

```ini
[TRANSLATE]
choose_template = 📝 Choose HTML template to send:
enter_subject = 📌 Enter email subject:
sending_start = 🚀 Starting to send...
success = ✅ Sent to: {email}
failure = ❌ Failed: {email} | Error: {error}
```

> 🌐 You can add new languages by creating `.ini` files in the `language/` folder.

---

## 📧 Recipient List — `emails.txt`

```txt
alice@example.com, bob@example.com, charlie@example.com
```

* Comma-separated
* One line only
* No need for newlines

---

## 💌 HTML Template

Example: `template/welcome.html`

```html
<!DOCTYPE html>
<html>
  <body>
    <h2 style="color: #00bfff;">Hi there 👋</h2>
    <p>This email was sent via Python & Flask 💌</p>
  </body>
</html>
```

> You can design your email with Canva or Figma, then export as `.html`.

---

## 🛠 Project Structure

```
📁 html-email-sender/
├── maildesk_web.py                   # Web UI (Flask)
├── __main__.py                       # CLI interface
├── config.ini                        # SMTP, Proxy, Language config
├── emails.txt                        # Recipients
├── template/                         # Email HTML templates
├── language/                         # Multi-language support
├── web/                              # Frontend assets (HTML, CSS, JS)
│   ├── index.html                    # Web interface
│   └── assets/
│       ├── css
│       │   ├── maildesk-ui.css       # Styled with Tailwind CSS
│       │   └── style.css             # Main Stylesheet
│       └── js
│           ├── main.js               # Main JS
│           └── security.js           # # Blocks DevTools, right-click, and copy/paste (anti-inspect script)
├── log/                              # Mail logs
└── setup-enviroment.bat              # Auto setup script (Windows)
```

---

## 🛡 How to Avoid Spam

| ❌ Avoid                      | ✅ Do This                          |
| ---------------------------- | ---------------------------------- |
| Image-heavy HTML             | Use lightweight HTML               |
| SHOUTY SUBJECTS!!!           | Write clean and calm subject lines |
| Sending 1 email to many BCCs | Send one-by-one (already handled)  |
| No sender name               | Use a friendly display name        |
| Using unknown SMTP servers   | Use Gmail, Mailgun, SendGrid, etc. |

---

## 🧙 Tips

* 🧪 Test multiple `.html` templates for A/B performance
* 🌐 Localize UI easily via `language/*.ini`
* 🔐 Use proxy if SMTP access is restricted
* ⚡ Fast and minimal, runs on any Python environment

---

## ✨ Credits

* Original CLI version by [Nyanko](https://github.com/Nyanko-Nya/html-email-sender)
* Web UI, Proxy & modern UX by the community 💖

> [☕ Buy me a boba](https://fe.wibu.me//img/QR.png) • Happy coding!

