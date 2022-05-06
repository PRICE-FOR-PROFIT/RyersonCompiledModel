from flask_marshmallow import Schema


class FreightSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["WeightClass0", "WeightClass1", "WeightClass200", "WeightClass500", "WeightClass1000", "WeightClass2000", "WeightClass5000", "WeightClass6500", "WeightClass10000", "WeightClass20000", "WeightClass24000", "WeightClass40000", "MinimumFreightCharge"]
