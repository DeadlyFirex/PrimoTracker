from marshmallow import Schema, fields


class AdminUserGetQuerySchema(Schema):
    expand = fields.Bool(required=False, default=False)
    fields = fields.List(fields.Str, required=False, default=[
        ""
    ])


class AdminUserGetPathSchema(Schema):
    uuid = fields.UUID(required=True)


class AdminUserDeleteQuerySchema(Schema):
    pass


class AdminUserDeletePathSchema(Schema):
    uuid = fields.UUID(required=True)
