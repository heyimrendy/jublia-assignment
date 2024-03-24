from threading import Thread

from celery import shared_task
from flask import current_app
from flask_mail import Message

from app.extensions import db, mail
from app.models import Email, Event


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


@shared_task(bind=True)
def save_email_task(self, id):
    email = db.session.query(Email).get(id)
    email.sent = True
    
    event = db.session.query(Event).filter(Event.id == email.event_id).first()
    if event is None:
        db.session.add(email)
        db.session.commit()
        return "Event not found"
    
    final_recipients = [user.email for user in event.users]
    if final_recipients:
        msg = Message(
            subject=email.email_subject,
            sender=("Admin", current_app.config["MAIL_SENDER"]),
            bcc=final_recipients,
            body=email.email_content,
            
        )
        Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
    else:
        print("No recipients, we won't send email")
    
    db.session.add(email)
    db.session.commit()

    return f"DONE SENDING SCHEDULED ID {id}"
