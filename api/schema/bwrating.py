from flask_marshmallow import Schema


class BwRatingSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "multi_market_name", "bellwether_material", "bw_rating_value", "bw_ratting_adder"]
