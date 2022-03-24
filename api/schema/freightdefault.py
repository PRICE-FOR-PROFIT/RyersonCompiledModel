from flask_marshmallow import Schema


class FreightDefaultSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "ship_plant", "state", "default_freight_charge_per_100_pounds", "default_minimum_freight_charge"]
