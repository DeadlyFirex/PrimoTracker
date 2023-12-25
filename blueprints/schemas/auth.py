from marshmallow import Schema, fields

from services.validation import validate_password, validate_alphanumeric


class AuthLoginBodySchema(Schema):
    username = fields.Str(required=True, validate=validate_alphanumeric)
    password = fields.Str(required=True, validate=validate_password)
