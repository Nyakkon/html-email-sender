from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from configparser import ConfigParser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import socket
import socks
import webbrowser
import threading
import time
from datetime import datetime

app = Flask(__name__, static_url_path='', static_folder='web', template_folder='web')

def read_config(path: str = "config.ini") -> ConfigParser:
    config = ConfigParser()
    if os.path.exists(path):
        config.read(path, encoding='utf-8')
    return config

def save_config(config: ConfigParser, path: str = "config.ini"):
    with open(path, 'w', encoding='utf-8') as f:
        config.write(f)

def log_to_file(message: str, filename: str = "log/maildesk_web.log"):
    os.makedirs("log", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

@app.route('/')
def index():
    return render_template('index.html')

def get_lang_messages(lang):
    if lang == 'vi':
        return {
            'sending': '⏳ Đang gửi email...\n',
            'success': '✅ Gửi email thành công!\n',
            'fail': '❌ Gửi email thất bại: {error}\n',
            'proxy_missing': '⚠️ Vui lòng nhập đầy đủ Proxy Host, Port, Type khi bật Proxy!\n',
            'log_success': '[{time}] Gửi tới: {email} ... Thành công!\n',
            'log_fail': '[{time}] Gửi tới: {email} ... Lỗi: {error}\n',
        }
    return {
        'sending': '⏳ Sending email...\n',
        'success': '✅ Email sent successfully!\n',
        'fail': '❌ Failed to send email: {error}\n',
        'proxy_missing': '⚠️ Please fill Proxy Host, Port, Type when Proxy is enabled!\n',
        'log_success': '[{time}] Sent to: {email} ... Success!\n',
        'log_fail': '[{time}] Sent to: {email} ... Error: {error}\n',
    }

@app.route('/api/lang')
def api_lang():
    config = read_config()
    lang = config.get('Language', 'lang', fallback='en')
    return jsonify(get_lang_messages(lang))

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    if request.method == 'POST':
        config = read_config()
        if 'SMTP' not in config:
            config.add_section('SMTP')
        config['SMTP']['server'] = request.form.get('smtp_server', '')
        config['SMTP']['port'] = request.form.get('smtp_port', '')
        config['SMTP']['username'] = request.form.get('smtp_username', '')
        config['SMTP']['password'] = request.form.get('smtp_password', '')
        config['SMTP']['display_name'] = request.form.get('display_name', '')
        if 'PROXY' not in config:
            config.add_section('PROXY')
        config['PROXY']['enabled'] = 'true' if request.form.get('proxy_enabled') == 'on' else 'false'
        config['PROXY']['type'] = request.form.get('proxy_type', '')
        config['PROXY']['host'] = request.form.get('proxy_host', '')
        config['PROXY']['port'] = request.form.get('proxy_port', '')
        if 'Language' not in config:
            config.add_section('Language')
        config['Language']['lang'] = request.form.get('language', 'en')
        save_config(config)
        return jsonify({'status': 'success'})
    config = read_config()
    return jsonify({
        'smtp': dict(config['SMTP']) if 'SMTP' in config else {},
        'proxy': dict(config['PROXY']) if 'PROXY' in config else {},
        'language': config.get('Language', 'lang', fallback='en')
    })

@app.route('/api/templates')
def get_templates():
    template_dir = './template'
    if not os.path.exists(template_dir):
        return jsonify([])
    templates = [f for f in os.listdir(template_dir) if f.endswith('.html')]
    return jsonify(templates)

@app.route('/api/template/<name>')
def get_template(name):
    template_path = os.path.join('./template', name)
    if not os.path.exists(template_path):
        return jsonify({'error': 'Template not found'}), 404
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return jsonify({'content': content})

@app.route('/api/send', methods=['POST'])
def send_email():
    config = read_config()
    lang = config.get('Language', 'lang', fallback='en')
    messages = get_lang_messages(lang)
    try:
        smtp_cfg = dict(config['SMTP'])
        if config.getboolean('PROXY', 'enabled', fallback=False):
            proxy_host = config.get('PROXY', 'host', fallback='')
            proxy_port = config.get('PROXY', 'port', fallback='')
            proxy_type = config.get('PROXY', 'type', fallback='socks5')
            if not proxy_host or not proxy_port or not proxy_type:
                return jsonify({'status': 'error', 'message': messages['proxy_missing']}), 400
            if proxy_type.lower() == 'https':
                socks_type = socks.HTTP
            else:
                socks_type = {
                    'socks5': socks.SOCKS5,
                    'socks4': socks.SOCKS4,
                    'http': socks.HTTP
                }.get(proxy_type.lower(), socks.SOCKS5)
            socks.set_default_proxy(socks_type, proxy_host, int(proxy_port))
            socket.socket = socks.socksocket
        data = request.json
        recipients = [e.strip() for e in data['to'].replace(' ', '').split(',') if e.strip()]
        all_success = True
        for email in recipients:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = data['subject']
            sender_name = smtp_cfg.get('display_name', smtp_cfg['username'])
            msg['From'] = formataddr((sender_name, smtp_cfg['username']))
            msg['To'] = email
            msg.attach(MIMEText(data['html_content'], 'html'))
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                with smtplib.SMTP(smtp_cfg['server'], int(smtp_cfg['port']), timeout=10) as server:
                    server.starttls()
                    server.login(smtp_cfg['username'], smtp_cfg['password'])
                    result = server.sendmail(smtp_cfg['username'], email, msg.as_string())
                if result:
                    all_success = False
                    log_line = messages['log_fail'].format(time=now, email=email, error=str(result)).strip()
                else:
                    log_line = messages['log_success'].format(time=now, email=email).strip()
                log_to_file(log_line)
            except Exception as e:
                all_success = False
                log_line = messages['log_fail'].format(time=now, email=email, error=str(e)).strip()
                log_to_file(log_line)
        if all_success:
            return jsonify({'status': 'success', 'message': messages['success']}), 200
        else:
            return jsonify({'status': 'error', 'message': messages['fail']}), 200
    except Exception as e:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log = messages['fail'].format(error=str(e))
        log = f'[{now}] {log}'
        log_to_file(log)
        return jsonify({'status': 'error', 'message': log}), 500
    
def open_browser():
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Timer(1.0, open_browser).start()
    app.run(debug=True)