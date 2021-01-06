from flask import current_app, render_template

from tasks import async_send_email


def send_email(to: str, subject: str, template: str, **kwargs) -> None:
    form_dict = {
        'subject': current_app.config['MAIL_SUBJECT_PREFIX'] + subject,
        'sender': current_app.config['MAIL_SENDER'],
        'recipients': [to],
        'body': render_template(template + '.txt', **kwargs),
        'html': render_template(template + '.html', **kwargs)
    }
    async_send_email.delay(form_dict)
