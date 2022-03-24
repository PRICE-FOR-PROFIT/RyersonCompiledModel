from flask_marshmallow import Schema


class ShipZoneSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "customer_id", "ship_plant", "zone"]
