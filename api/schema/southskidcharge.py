from flask_marshmallow import Schema


class SouthSkidChargeSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "product", "form", "weight_per_skid", "skid_charge"]
