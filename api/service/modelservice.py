from api.model.model import ModelModel
from api.model.parameter import ParameterModel


class ModelService:
    def get_model(self, model_id: str, debug_mode: bool) -> ModelModel:
        model = ModelModel()

        if model_id.casefold() == "recommendedprice":
            model.name = "RecommendedPrice"
            model.calculations = []
            model.debug_mode = debug_mode
            model.model_inputs = []
            model.version = 3
            model.is_active = True
            model.id = "RecommendedPrice"

            model.model_inputs.append(ParameterModel("quoteLines", "array", True, None))
            model.model_inputs.append(ParameterModel("customerId", "string", True, None))
            model.model_inputs.append(ParameterModel("shipToZipCode", "string", False, ""))
            model.model_inputs.append(ParameterModel("shipToState", "string", False, ""))
            model.model_inputs.append(ParameterModel("salesOffice", "string", False, "NA"))
            model.model_inputs.append(ParameterModel("independentCalculationFlag", "bool", False, "False"))
            model.model_inputs.append(ParameterModel("automatedTuningGroupOverride", "string", False, ""))
            model.model_inputs.append(ParameterModel("automatedTuningFlagOverride", "string", False, ""))
        else:
            model.name = "quoteLineSAP"
            model.calculations = []
            model.debug_mode = debug_mode
            model.model_inputs = []
            model.version = 40
            model.is_active = True
            model.id = "quoteLineSAP"

            model.model_inputs.append(ParameterModel("material", "string", True, None))
            model.model_inputs.append(ParameterModel("itemNumber", "string", True, None))
            model.model_inputs.append(ParameterModel("shipPlant", "string", False, None))
            model.model_inputs.append(ParameterModel("stockPlant", "string", True, None))
            model.model_inputs.append(ParameterModel("weight", "double", True, None))
            model.model_inputs.append(ParameterModel("opCode", "string", False, ""))
            model.model_inputs.append(ParameterModel("netWeightOfSalesItem", "double", False, "-1.0"))
            model.model_inputs.append(ParameterModel("netWeightPerFinishedPiece", "double", False, "0.0"))
            model.model_inputs.append(ParameterModel("bundles", "int", False, "-1"))
            model.model_inputs.append(ParameterModel("totalQuotePounds", "double", True, None))
            model.model_inputs.append(ParameterModel("automatedTuningGroupOverride", "string", False, ""))
            model.model_inputs.append(ParameterModel("automatedTuningFlagOverride", "string", False, ""))

        return model


