from flask_mail import Message

from celery_app import celery
from models.extensions import mail


@celery.task
def async_send_email(form: dict) -> None:
    msg = Message(
        form['subject'],
        sender=form['sender'],
        recipients=form['recipients']
    )
    msg.body = form['body']
    msg.html = form['html']
    mail.send(msg)
