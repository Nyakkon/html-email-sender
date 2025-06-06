import smtplib
import os
import re
import sys
from configparser import ConfigParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr


def read_config(path: str = "config.ini") -> ConfigParser:
    config = ConfigParser()
    
    if not os.path.exists(path):
        print(f"Could not relsove path {path}")
        sys.exit(1)

    with open(file = path, mode = "r", encoding = "utf-8") as configFile:
        config.read_file(configFile)

    return config

def read_language(lang_code: str = "en") -> dict[str, str]:
    lang_path: str = f"language/{lang_code}.ini"

    if not os.path.exists(lang_path):
        print(f"⚠️ Language file '{lang_path}' not found. Falling back to English.")
        lang_path = "language/en.ini"

    lang = ConfigParser()
    with open(file = lang_path, mode = "r", encoding = "utf-8") as configLanguage:
        lang.read_file(configLanguage)

    return dict(lang["TRANSLATE"])

def read_emails(path: str = "emails.txt") -> list[str]:
    if not os.path.exists(path):
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        emails = [e.strip() for e in re.split(r",\s*", content) if e.strip()]
        return emails

def list_html_templates(folder: str  = "./template"):
    if not os.path.exists(folder):
        print(f"Could not relolv HTML temlate folder {folder}")
        sys.exit(1)

    return [f for f in os.listdir(folder) if f.endswith(".html")]

def choose_template(templates: list[str], lang: dict[str, str]) -> str:
    prompt_text = lang.get("choose_template", "Please choose template")
    print(prompt_text)

    for idx, name in enumerate(templates):
        print(f"{idx + 1}. {name}")

    while True:
        choice = input(lang["choose_template_input"] + " ")

        if choice.isdigit() and 1 <= int(choice) <= len(templates):
            return templates[int(choice) - 1]
        
        print(lang.get("invalid_choice"))

def send_email(smtp_cfg: dict[str, str], receiver: str, subject: str, html_content: str, lang: dict[str, str]):
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

        print(lang["success"].format(email = receiver))

    except Exception as exception:
        print(lang["failure"].format(email = receiver, error = exception))

def main():
    config = read_config()
    smtp_cfg = dict(config["SMTP"])
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

    print("\n" + lang["sending_start"].format(count = len(emails)) + "\n")
    for email in emails:
        send_email(smtp_cfg, email, subject, html_content, lang)

if __name__ == "__main__":
    main()
