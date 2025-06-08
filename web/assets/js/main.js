function isValidEmail(email) {
    return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)
        && !/\.\./.test(email)
        && !email.startsWith('.')
        && !email.endsWith('.')
        && !email.includes('..@')
        && !email.includes('@..');
}
function validateEmails(emailString) {
    const emails = emailString.split(',').map(e => e.trim()).filter(e => e);
    return emails.every(isValidEmail);
}
let langMsg = {sending: 'Sending...'};
async function fetchLangMsg() {
    try {
        const langRes = await fetch('/api/lang');
        if (langRes.ok) langMsg = await langRes.json();
    } catch {}
}
document.addEventListener('DOMContentLoaded', async () => {
    await fetchLangMsg();
    await loadTemplates(); // <-- Gọi luôn khi vào trang
    const sendTab = document.getElementById('send-tab');
    const settingsTab = document.getElementById('settings-tab');
    const sendContent = document.getElementById('send');
    const settingsContent = document.getElementById('settings');
    
    async function loadSettings() {
        try {
            const res = await fetch('/api/settings');
            if (!res.ok) return;
            const data = await res.json();
            if (data.smtp) {
                document.getElementById('smtp_server').value = data.smtp.server || '';
                document.getElementById('smtp_port').value = data.smtp.port || '';
                document.getElementById('smtp_username').value = data.smtp.username || '';
                document.getElementById('smtp_password').value = data.smtp.password || '';
                document.getElementById('display_name').value = data.smtp.display_name || '';
            }
            if (data.proxy) {
                document.getElementById('proxy_enabled').checked = data.proxy.enabled === 'true';
                document.getElementById('proxy_type').value = data.proxy.type || 'socks5';
                document.getElementById('proxy_host').value = data.proxy.host || '';
                document.getElementById('proxy_port').value = data.proxy.port || '';
            }
            if (data.language) {
                document.getElementById('language').value = data.language || 'en';
            }
        } catch (e) {}
    }
    
    async function loadTemplates() {
        try {
            const res = await fetch('/api/templates');
            if (!res.ok) return;
            const templates = await res.json();
            const templateSelect = document.getElementById('template');
            templateSelect.innerHTML = '<option value="">Select a template...</option>';
            templates.forEach(name => {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name;
                templateSelect.appendChild(opt);
            });
        } catch (e) {}
    }
    sendTab.addEventListener('click', async () => {
        sendTab.classList.add('nav-tab-active');
        settingsTab.classList.remove('nav-tab-active');
        sendContent.classList.remove('hidden');
        settingsContent.classList.add('hidden');
        await loadTemplates();
    });
    settingsTab.addEventListener('click', async () => {
        settingsTab.classList.add('nav-tab-active');
        sendTab.classList.remove('nav-tab-active');
        settingsContent.classList.remove('hidden');
        sendContent.classList.add('hidden');
        await loadSettings();
    });
    document.getElementById('language').addEventListener('change', async () => {
        await fetchLangMsg();
    });
    document.getElementById('template').addEventListener('change', async (e) => {
        if (e.target.value) {
            try {
                const response = await fetch(`/api/template/${e.target.value}`);
                const data = await response.json();
                document.getElementById('htmlContent').value = data.content;
            } catch (error) {
                Swal.fire('Error', 'Failed to load template', 'error');
            }
        }
    });
    document.getElementById('htmlFile').addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            document.getElementById('htmlContent').value = event.target.result;
        };
        reader.readAsText(file);
    });
    document.getElementById('importEmailFile').addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const ext = file.name.split('.').pop().toLowerCase();
        let text = '';
        if (['csv', 'txt', 'html'].includes(ext)) {
            text = await file.text();
        } else if (['xls', 'xlsx'].includes(ext)) {
            const data = await file.arrayBuffer();
            const workbook = XLSX.read(data, {type: 'array'});
            let allText = '';
            workbook.SheetNames.forEach(name => {
                const ws = workbook.Sheets[name];
                allText += XLSX.utils.sheet_to_csv(ws) + '\n';
            });
            text = allText;
        } else {
            Swal.fire('Lỗi', 'Chỉ hỗ trợ file csv, txt, html, xls, xlsx.', 'error');
            return;
        }
        let emails = Array.from(new Set((text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g) || []).map(e => e.trim().toLowerCase())));
        emails = emails.filter(isValidEmail);
        if (emails.length === 0) {
            Swal.fire('Lỗi', 'Không tìm thấy email hợp lệ trong file.', 'error');
            return;
        }
        const toInput = document.getElementById('to');
        const current = toInput.value.split(',').map(e => e.trim().toLowerCase()).filter(isValidEmail);
        const all = Array.from(new Set([...current, ...emails]));
        toInput.value = all.join(', ');
        Swal.fire('Thành công', `Đã nhập ${emails.length} email hợp lệ từ file.`, 'success');
    });
    document.getElementById('settingsForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const proxyEnabled = document.getElementById('proxy_enabled').checked;
        const proxyHost = document.getElementById('proxy_host').value.trim();
        const proxyPort = document.getElementById('proxy_port').value.trim();
        const proxyType = document.getElementById('proxy_type').value.trim();
        if (proxyEnabled && (!proxyHost || !proxyPort || !proxyType)) {
            Swal.fire('Lỗi', 'Vui lòng nhập đầy đủ Proxy Host, Port, Type khi bật Proxy.', 'error');
            return;
        }
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                Swal.fire('Success', 'Settings saved successfully', 'success');
            } else {
                throw new Error('Failed to save settings');
            }
        } catch (error) {
            Swal.fire('Error', 'Failed to save settings', 'error');
        }
    });
    document.getElementById('sendEmailForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const toValue = document.getElementById('to').value;
        const templateValue = document.getElementById('template').value;
        const htmlContentValue = document.getElementById('htmlContent').value.trim();
        if (!validateEmails(toValue)) {
            Swal.fire('Lỗi', langMsg['fail'] || 'Vui lòng nhập đúng định dạng email, cách nhau bằng dấu phẩy.', 'error');
            return;
        }
        if (!templateValue && !htmlContentValue) {
            Swal.fire('Lỗi', 'Vui lòng chọn template hoặc nhập nội dung HTML.', 'error');
            return;
        }
        const data = {
            to: toValue,
            subject: document.getElementById('subject').value,
            html_content: htmlContentValue
        };
        document.getElementById('send-btn').disabled = true;
        document.getElementById('settings-tab').disabled = true;
        Array.from(document.querySelectorAll('#sendEmailForm input, #sendEmailForm select, #sendEmailForm textarea')).forEach(el => el.disabled = true);
        document.getElementById('send-spinner').style.display = '';
        document.getElementById('send-btn-text').textContent = 'Sending...';
        try {
            const response = await fetch('/api/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (response.ok) {
                Swal.fire('Success', langMsg.success || 'Email sent successfully', 'success');
                e.target.reset();
            } else {
                throw new Error(result.message || langMsg.fail || 'Failed to send email');
            }
        } catch (error) {
            Swal.fire('Error', error.message || langMsg.fail || 'Failed to send email', 'error');
        }
        document.getElementById('send-btn').disabled = false;
        document.getElementById('settings-tab').disabled = false;
        Array.from(document.querySelectorAll('#sendEmailForm input, #sendEmailForm select, #sendEmailForm textarea')).forEach(el => el.disabled = false);
        document.getElementById('send-spinner').style.display = 'none';
        document.getElementById('send-btn-text').textContent = 'Send Email';
    });
}); 