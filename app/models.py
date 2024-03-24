from __future__ import annotations
from typing import List

import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


user_event_association = sqlalchemy.Table(
    "user_event_association",
    db.metadata,
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id")),
    sqlalchemy.Column(
        "event_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("event.id")
    ),
)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(sqlalchemy.String(120), index=True, unique=True)
    events: Mapped[List[Event]] = relationship(
        secondary=user_event_association, back_populates="users"
    )

    def to_dict(self):
        data = {"id": self.id, "email": self.email}
        return data


class Event(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sqlalchemy.String(255), nullable=False)
    users: Mapped[List[User]] = relationship(
        secondary=user_event_association, back_populates="events"
    )


class Email(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(sqlalchemy.ForeignKey(Event.id), index=True)
    email_subject: Mapped[str] = mapped_column(sqlalchemy.String(255), nullable=False)
    email_content: Mapped[str] = mapped_column(sqlalchemy.Text, nullable=False)
    timestamp: Mapped[int] = mapped_column(sqlalchemy.BigInteger, nullable=False)
    sent: Mapped[bool] = mapped_column(default=False)
