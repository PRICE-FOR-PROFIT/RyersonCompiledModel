from flask_marshmallow import Schema


class PackagingCostSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "overhead_group", "overhead_group_name", "unit_handling_cost", "per_ton_packaging_cost", "per_ton_stocking_cost"]
