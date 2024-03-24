import datetime

from flask import request
from marshmallow import ValidationError, EXCLUDE
import sqlalchemy

from app.api import bp
from app.api.errors import error_response
from app.dto import EmailSchema, EventSchema, SubsribeEventSchema, UserSchema
from app.extensions import db
from app.models import Event, Email, User
from app.tasks import save_email_task


@bp.route("/events", methods=["POST"])
def create_event():
    data = request.get_json()
    schema = EventSchema(unknown=EXCLUDE)

    try:
        schema.load(data)
    except ValidationError as err:
        return error_response(400, err.messages)

    event = Event(name=data["name"])

    db.session.add(event)
    db.session.commit()

    return {
        "message": "Event created successfully",
        "user": {"id": event.id, "email": event.name},
    }


@bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    schema = UserSchema(unknown=EXCLUDE)

    try:
        schema.load(data)
    except ValidationError as err:
        return error_response(400, err.messages)

    if db.session.scalar(sqlalchemy.select(User).where(User.email == data["email"])):
        return error_response(409, {"email": ["Email address already exist."]})
    user = User(email=data["email"])

    db.session.add(user)
    db.session.commit()
    return {
        "message": "User created successfully",
        "user": {"id": user.id, "email": user.email},
    }


@bp.route("/user/<int:id>/events", methods=['GET'])
def get_subscriptions(id):
    user = db.session.scalar(sqlalchemy.select(User).where(User.id == id))
    if user is None:
        return error_response(404, {"user": [f"User with id {id} not found."]})
    
    events = [{"id": event.id, "name": event.name} for event in user.events]

    return {"events": events}



@bp.route("/subscribe", methods=["POST"])
def subsribe_event():
    data = request.get_json()
    schema = SubsribeEventSchema(unknown=EXCLUDE)

    try:
        schema.load(data)
    except ValidationError as err:
        return error_response(400, err.messages)

    user = db.session.scalar(sqlalchemy.select(User).where(User.email == data["email"]))
    if user is None:
        return error_response(404, {"email": ["Email address not found."]})

    event = db.session.scalar(
        sqlalchemy.select(Event).where(Event.id == data["event_id"])
    )
    if event is None:
        return error_response(
            404, {"event_id": [f"Event id {data['event_id']} not found."]}
        )

    if event in user.events:
        return error_response(
            409,
            {
                "event_id": [
                    f"You already subscribed to the event id {data['event_id']}."
                ]
            },
        )

    user.events.append(event)
    db.session.commit()

    return {
        "message": "Successfully subscribed to the event",
        "event": {"id": event.id, "name": event.name},
    }


@bp.route("/unsubscribe", methods=["POST"])
def unsubsribe_event():
    data = request.get_json()
    schema = SubsribeEventSchema(unknown=EXCLUDE)

    try:
        schema.load(data)
    except ValidationError as err:
        return error_response(400, err.messages)

    user = db.session.scalar(sqlalchemy.select(User).where(User.email == data["email"]))
    if user is None:
        return error_response(404, {"email": ["Email address not found."]})

    event = db.session.scalar(
        sqlalchemy.select(Event).where(Event.id == data["event_id"])
    )
    if event is None:
        return error_response(
            404, {"event_id": [f"Event id {data['event_id']} not found."]}
        )

    if user not in event.users:
        return error_response(
            404, {"users": [f"You're not subsribed to the event id {data['event_id']}"]}
        )

    event.users.remove(user)
    db.session.commit()

    return {
        "message": "Successfully unsubscribed to the event",
        "event": {"id": event.id, "name": event.name},
    }


@bp.route("/save_emails", methods=["POST"])
def save_email():
    data = request.get_json()
    schema = EmailSchema(unknown=EXCLUDE)

    try:
        schema.load(data)
    except ValidationError as err:
        return error_response(400, err.messages)

    if (
        db.session.scalar(sqlalchemy.select(Event).where(Event.id == data["event_id"]))
        is None
    ):
        return error_response(
            404, {"event_id": [f"Event id {data['event_id']} not found."]}
        )

    data_timestamp = int(
        datetime.datetime.fromisoformat(f"{data['timestamp']}:00+08:00").timestamp()
    )
    email = Email(
        event_id=data["event_id"],
        email_subject=data["email_subject"],
        email_content=data["email_content"],
        timestamp=data_timestamp,
    )

    db.session.add(email)
    db.session.commit()

    # print(data_timestamp)
    # print(datetime.datetime.now( datetime.timezone(datetime.timedelta(hours=8)) ))
    # dt_jst_aware = datetime.datetime.fromtimestamp(1711269984, datetime.timezone(datetime.timedelta(hours=8)))
    # print(dt_jst_aware)

    save_email_task.apply_async(args=[email.id], eta=datetime.datetime.fromisoformat(f"{data['timestamp']}:00+08:00"))

    return {"message": "Email saved and will be sent as scheduled"}
