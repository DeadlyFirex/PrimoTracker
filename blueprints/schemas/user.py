from marshmallow import Schema, fields


class UserGetQuerySchema(Schema):
    expand = fields.Bool(required=False, default=False)
    fields = fields.List(fields.Str, required=False, default=[
        ""
    ])
