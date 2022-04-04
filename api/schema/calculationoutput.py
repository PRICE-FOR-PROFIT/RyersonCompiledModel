from flask_marshmallow import Schema


class CalculationOutputSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["Name", "Passthrough", "Value"]
