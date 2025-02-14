import traitlets as tl
from aiidalab_qe.common.mixins import HasInputStructure
from aiidalab_qe.common.panel import ConfigurationSettingsModel


class ConfigurationSettingsModel(ConfigurationSettingsModel, HasInputStructure):
    title = "Bader charge"
    identifier = "bader"

    dependencies = [
        "input_structure",
        "workchain.protocol",
    ]

    protocol = tl.Unicode(allow_none=True)
    electronic_type = tl.Unicode(allow_none=True)

    def get_model_state(self):
        return {}

    def set_model_state(self, parameters: dict):
        """"""
