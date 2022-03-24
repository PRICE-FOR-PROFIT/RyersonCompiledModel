from flask_marshmallow import Schema


class AutomatedTuningSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["unique_id", "product", "condensed_form", "location_group", "salt_value", "price_up_active_flag", "price_up_measurement_level", "price_up_concentration", "price_up_magnitude", "price_up_realization", "price_up_min_win_rate_diff", "price_up_sig_level", "price_up_power", "price_up_obs_req", "price_down_active_flag", "price_down_measurement_level", "price_down_concentration", "price_down_magnitude", "price_down_realization", "price_down_min_win_rate_diff", "price_down_sig_level", "price_down_power", "price_down_obs_req"]
