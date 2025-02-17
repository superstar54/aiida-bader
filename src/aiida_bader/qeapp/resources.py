"""Panel for Bader plugin."""

from aiidalab_qe.common.code.model import CodeModel, PwCodeModel
from aiidalab_qe.common.panel import (
    PluginResourceSettingsModel,
    PluginResourceSettingsPanel,
)


class ResourceSettingsModel(PluginResourceSettingsModel):
    """Model for the bader code setting plugin."""

    title = "Bader charge"
    identifier = "bader"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_models(
            {
                "pw": PwCodeModel(
                    name="pw.x",
                    description="pw.x",
                    default_calc_job_plugin="quantumespresso.pw",
                ),
                "pp": CodeModel(
                    name="pp.x",
                    description="pp.x",
                    default_calc_job_plugin="quantumespresso.pp",
                ),
                "bader": CodeModel(
                    name="bader",
                    description="bader",
                    default_calc_job_plugin="bader.bader",
                ),
            }
        )


class ResourceSettingsPanel(
    PluginResourceSettingsPanel[ResourceSettingsModel],
):
    """Panel for configuring the wannier90 plugin."""
