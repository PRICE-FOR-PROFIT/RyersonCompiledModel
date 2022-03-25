from flask_marshmallow import Schema
from marshmallow.fields import Dict


class ResponseWrapperWithMetaSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["data", "metadata"]

    data = Dict()
    metadata = Dict()
