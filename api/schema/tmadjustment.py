from flask_marshmallow import Schema


class TmAdjustmentSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "multi_market_name", "product", "form", "weight_class_1", "weight_class_200", "weight_class_500", "weight_class_1000", "weight_class_2000", "weight_class_5000", "weight_class_6500", "weight_class_10000", "weight_class_20000", "weight_class_24000", "weight_class_40000"]
