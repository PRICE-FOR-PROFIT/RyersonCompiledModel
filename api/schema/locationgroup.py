from flask_marshmallow import Schema


class LocationGroupSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "rc_mapping", "location_group_value", "region"]
