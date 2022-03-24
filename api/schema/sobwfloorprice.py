from flask_marshmallow import Schema


class SoBwFloorPriceSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "isr_office", "bellwether_material", "floor_price"]
