import datetime
from marshmallow import Schema, fields, validate, ValidationError, validates


def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


class EventSchema(Schema):
    name = fields.Str(
        required=True, validate=[must_not_be_blank, validate.Length(max=255)]
    )


class UserSchema(Schema):
    email = fields.Email(required=True)


class SubsribeEventSchema(Schema):
    email = fields.Email(required=True)
    event_id = fields.Integer(required=True)


class EmailSchema(Schema):
    event_id = fields.Integer(required=True)
    email_subject = fields.Str(
        required=True, validate=[must_not_be_blank, validate.Length(max=255)]
    )
    email_content = fields.Str(required=True, validate=[must_not_be_blank])
    timestamp = fields.DateTime(format="%Y-%m-%d %H:%M", required=True)

    @validates("timestamp")
    def validate_timestamp(self, value):
        current_timestamp = (
            datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
            .replace(microsecond=0, second=0)
            .timestamp()
        )
        value_timestamp = value.replace(
            tzinfo=datetime.timezone(datetime.timedelta(hours=8))
        ).timestamp()
        print(value_timestamp)
        if value_timestamp < current_timestamp:
            raise ValidationError("Given datetime is lower than current datetime.")
