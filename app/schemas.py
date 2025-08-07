from datetime import datetime
from marshmallow import Schema, fields, ValidationError, validate


def validate_date(date):
    try:
        datetime.strptime(date, '%Y-%m-%d_%H:%M')
    except ValueError:
        raise ValidationError(
            "Формат даты - YYYY-MM-DD_HH:mm"
        )

class FileRecordSchema(Schema):
    name = fields.Str(required=True)
    date = fields.DateTime(format="%Y-%m-%d_%H:%M", required=True)
