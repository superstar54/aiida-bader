import traitlets as tl
from aiidalab_qe.common.mixins import HasInputStructure
from aiidalab_qe.common.panel import ConfigurationSettingsModel
from aiida.orm import QueryBuilder, Group

BASE_URL = "https://github.com/superstar54/aiida-bader/raw/main/data/"


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

    def _pseudo_group_exists(self, group_label):
        groups = (
            QueryBuilder()
            .append(
                Group,
                filters={"label": group_label},
            )
            .all(flat=True)
        )
        return len(groups) > 0 and len(groups[0].nodes) > 0

    def install_pseudos(self):
        import os
        from pathlib import Path
        from subprocess import run

        for pseudo_group in self.pseudo_group_options:
            if not self._pseudo_group_exists(pseudo_group):
                url = BASE_URL + pseudo_group + ".aiida"

                env = os.environ.copy()
                env["PATH"] = f"{env['PATH']}:{Path.home().joinpath('.local', 'bin')}"

                def run_(*args, **kwargs):
                    return run(
                        *args, env=env, capture_output=True, check=True, **kwargs
                    )

                run_(["verdi", "archive", "import", url, "--no-import-group"])
