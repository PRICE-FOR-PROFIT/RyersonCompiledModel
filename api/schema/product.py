from flask_marshmallow import Schema


class ProductSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "rc_mapping", "material", "bellwether_material", "product_name", "form", "index", "bellwether_base_cost", "market_movement_adder", "percent_adjustment", "dollar_adjustment", "modeled_cost", "unit_handling_cost", "per_ton_packaging_cost", "per_ton_stocking_cost", "material_description", "exchange_rate"]
