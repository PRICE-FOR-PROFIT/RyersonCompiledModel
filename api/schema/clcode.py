from flask_marshmallow import Schema


class ClCodeSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "customer_number", "customer_sales_office", "product", "form", "cl_code_value", "cl_discount"]
