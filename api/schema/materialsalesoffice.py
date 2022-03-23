from flask_marshmallow import Schema


class MaterialSalesOfficeSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "material", "isr_office", "start_effective_date", "end_effective_date", "red_margin_threshold", "yellow_margin_threshold", "price_adjustment"]
