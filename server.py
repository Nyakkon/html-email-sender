import smtplib
import os
import re
from configparser import ConfigParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

def read_config(path="config.ini"):
    config = ConfigParser()
    with open(path, "r", encoding="utf-8") as f:
        config.read_file(f)
    return config

def read_language(lang_code="en"):
    lang_path = f"language/{lang_code}.ini"
    if not os.path.exists(lang_path):
        print(f"⚠️ Language file '{lang_path}' not found. Falling back to English.")
        lang_path = "language/en.ini"
    lang = ConfigParser()
    with open(lang_path, "r", encoding="utf-8") as f:
        lang.read_file(f)
    return lang["TRANSLATE"]

def read_emails(path="emails.txt"):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        emails = [e.strip() for e in re.split(r",\s*", content) if e.strip()]
        return emails

def list_html_templates(folder="./template"):
    return [f for f in os.listdir(folder) if f.endswith(".html")]

def choose_template(templates, lang):
    print(lang["choose_template"])
    for idx, name in enumerate(templates):
        print(f"{idx + 1}. {name}")
    while True:
        choice = input(lang["choose_template_input"] + " ")
        if choice.isdigit() and 1 <= int(choice) <= len(templates):
            return templates[int(choice) - 1]
        print(lang["invalid_choice"])

def send_email(smtp_cfg, receiver, subject, html_content, lang):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    sender_name = smtp_cfg.get("display_name", smtp_cfg["username"])
    msg["From"] = formataddr((sender_name, smtp_cfg["username"]))
    msg["To"] = receiver
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(smtp_cfg["server"], int(smtp_cfg["port"])) as server:
            server.starttls()
            server.login(smtp_cfg["username"], smtp_cfg["password"])
            server.sendmail(smtp_cfg["username"], receiver, msg.as_string())
        print(lang["success"].format(email=receiver))
    except Exception as e:
        print(lang["failure"].format(email=receiver, error=e))

def main():
    config = read_config()
    smtp_cfg = config["SMTP"]
    lang_code = config["Language"]["lang"] if "Language" in config and "lang" in config["Language"] else "en"
    lang = read_language(lang_code)

    emails = read_emails()
    if not emails:
        print(lang["email_not_found"])
        return

    subject = input(lang["enter_subject"] + " ")

    templates = list_html_templates()
    if not templates:
        print(lang["template_not_found"])
        return

    chosen_template = choose_template(templates, lang)
    with open(os.path.join("template", chosen_template), "r", encoding="utf-8") as f:
        html_content = f.read()

    print("\n" + lang["sending_start"].format(count=len(emails)) + "\n")
    for email in emails:
        send_email(smtp_cfg, email, subject, html_content, lang)

if __name__ == "__main__":
    main()
