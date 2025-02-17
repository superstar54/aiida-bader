import traitlets as tl
from aiidalab_qe.common.mixins import HasInputStructure
from aiidalab_qe.common.panel import ConfigurationSettingsModel
from aiida.orm import QueryBuilder, Group


class ConfigurationSettingsModel(ConfigurationSettingsModel, HasInputStructure):
    title = "Bader charge"
    identifier = "bader"

    dependencies = [
        "input_structure",
        "workchain.protocol",
        "advanced.pseudos.functional",
    ]

    protocol = tl.Unicode(allow_none=True)
    electronic_type = tl.Unicode(allow_none=True)
    functional = tl.Unicode()
    pseudo_group_options = tl.List(
        trait=tl.Unicode(),
        default_value=[
            "psl_kjpaw_pbe",
            "psl_kjpaw_pbesol",
        ],
    )
    pseudo_group = tl.Unicode("psl_kjpaw_pbesol")

    def get_model_state(self):
        return {
            "pseudo_group": self.pseudo_group,
        }

    def set_model_state(self, parameters: dict):
        """"""
        self.pseudo_group = parameters.get("pseudo_group", self.pseudo_group)
