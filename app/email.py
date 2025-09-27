from flask import render_template

def send_email(to, subject, template, **kwargs):
    # نولّد النصوص من القوالب
    text_body = render_template(template + '.txt', **kwargs)
    html_body = render_template(template + '.html', **kwargs)

    # ✅ للتجربة فقط: نطبع الرسالة في الطرفية بدل الإرسال
    print("=== Simulated Email ===")
    print("To:", to)
    print("Subject:", subject)
    print("Text Body:\n", text_body)
    print("HTML Body:\n", html_body)
    print("=======================")
