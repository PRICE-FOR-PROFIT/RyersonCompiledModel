from flask_marshmallow import Schema


class IdoSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "stock_plant", "ship_plant", "ido_per_pound", "ido_min", "ido_max"]
