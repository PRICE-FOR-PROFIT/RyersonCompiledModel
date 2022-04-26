from flask_marshmallow import Schema


class CostAdjustmentSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["product", "cost", "form", "material", "material_classification", "material_description", "stock_plant", "target_margin", "unique_id"]
