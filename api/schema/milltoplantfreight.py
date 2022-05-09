from flask_marshmallow import Schema


class MillToPlantFreightSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "bellwether_material", "ship_plant", "mill_to_plant_freight_value"]
