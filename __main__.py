import socks
import socket
import smtplib
import os
import re
import sys
from configparser import ConfigParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import datetime

def log_to_file(message: str, filename: str = "log/proxy.log"):
    os.makedirs("log", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

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

def configure_proxy(config, language):
    if config.has_section("PROXY") and config.getboolean("PROXY", "enabled", fallback=False):
        proxy_host = config.get("PROXY", "host", fallback="")
        proxy_port = config.get("PROXY", "port", fallback="")
        proxy_type = config.get("PROXY", "type", fallback="socks5")

        if not proxy_host.strip() or not proxy_port.strip():
            msg = language.get("proxy_skip_warning", "⚠️ Proxy enabled but host or port is empty. Skipping proxy setup.")
            print(msg)
            log_to_file("SKIP: Proxy enabled but host or port missing.")
            return

        try:
            socks_type = {
                "socks5": socks.SOCKS5,
                "socks4": socks.SOCKS4,
                "http": socks.HTTP
            }.get(proxy_type.lower(), socks.SOCKS5)

            socks.set_default_proxy(socks_type, proxy_host, int(proxy_port))
            socket.socket = socks.socksocket

            msg = language.get("proxy_success", "✅ Proxy connected successfully.")
            print(msg)
            log_to_file(f"CONNECTED: Proxy {proxy_type.upper()} at {proxy_host}:{proxy_port}")
        except Exception as e:
            err_msg = language.get("proxy_fail", "❌ Failed to connect to proxy. Error: {error}").format(error=str(e))
            print(err_msg)
            log_to_file(f"ERROR: Failed to connect to proxy - {type(e).__name__}: {str(e)}")


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
    import socket

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    sender_name = smtp_cfg.get("display_name", smtp_cfg["username"])
    msg["From"] = formataddr((sender_name, smtp_cfg["username"]))
    msg["To"] = receiver
    msg.attach(MIMEText(html_content, "html"))

    try:
        print(lang.get("smtp_connecting", "🟡 Connecting to SMTP server to send mail to {email}...").format(email=receiver))

        smtp_host = smtp_cfg["server"]
        smtp_port = int(smtp_cfg["port"])
        ipv4_addrs = [ai[4][0] for ai in socket.getaddrinfo(smtp_host, smtp_port, socket.AF_INET)]
        if not ipv4_addrs:
            raise Exception(lang.get("smtp_no_ipv4", "❌ No IPv4 address found for SMTP host."))

        smtp_ip = ipv4_addrs[0]
        print(lang.get("smtp_resolved", "📡 {host} resolved to IPv4: {ip}").format(host=smtp_host, ip=smtp_ip))


        with smtplib.SMTP(smtp_ip, smtp_port, timeout=10) as server:
            print(lang.get("smtp_tls", "🔐 Starting TLS..."))
            server.starttls()
            print(lang.get("smtp_login", "🔑 Logging in..."))
            server.login(smtp_cfg["username"], smtp_cfg["password"])
            print(lang.get("smtp_sending", "📨 Sending mail..."))
            server.sendmail(smtp_cfg["username"], receiver, msg.as_string())

        print(lang["success"].format(email=receiver))

    except Exception as exception:
        print(lang["failure"].format(email=receiver, error=exception))


def main():
    config = read_config()
    smtp_cfg = dict(config["SMTP"])
    lang_code = config["Language"]["lang"] if "Language" in config and "lang" in config["Language"] else "en"
    lang = read_language(lang_code)

    configure_proxy(config, lang)

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