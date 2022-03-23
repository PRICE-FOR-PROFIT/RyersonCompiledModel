from flask_marshmallow import Schema


class CustomerSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "customer_number", "sap_ind", "multi_market_name", "customer_sales_office", "isr_office", "customer_name", "rc_mapping", "dso", "waive_skid", "dso_adder", "percent_adder", "dollar_adder"]
        