from flask_marshmallow import Schema
from marshmallow.fields import Dict


class ErrorWrapperWithMetaSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["error", "metadata"]

    error = Dict()
    metadata = Dict()
