"""Panel for bader plugin."""

from aiidalab_qe.common.panel import ConfigurationSettingsPanel
import ipywidgets as ipw
from .model import ConfigurationSettingsModel
from aiidalab_qe.common.infobox import InAppGuide

PSEUDO_PSL_URL = "https://pseudopotentials.quantum-espresso.org/legacy_tables"


class ConfigurationSettingPanel(
    ConfigurationSettingsPanel[ConfigurationSettingsModel],
):
    def __init__(self, model: ConfigurationSettingsModel, **kwargs):
        super().__init__(model, **kwargs)

        # error message
        self.error_message = ipw.HTML()
        # Warning message
        self.warning_message = ipw.HTML()

    def render(self):

        if self.rendered:
            return

        self._model.install_pseudos()

        self.pseudo_group = ipw.Dropdown(
            description="Group:",
            style={"description_width": "initial"},
        )
        ipw.dlink(
            (self._model, "pseudo_group_options"),
            (self.pseudo_group, "options"),
        )
        ipw.link(
            (self._model, "pseudo_group"),
            (self.pseudo_group, "value"),
        )

        self.children = [
            self.error_message,
            self.warning_message,
            InAppGuide(identifier="bader-settings"),
            ipw.HTML(
                """
                <div style="margin-top: 15px;">
                    <h4>Pseudopotential group</h4>
                </div>
            """
            ),
            ipw.HTML(
                f"""
                <div style="line-height: 140%; margin-bottom: 10px">
                    Please select a pseudopotential group.
                    The pseudopotentials are downloaded from this <a href="{PSEUDO_PSL_URL}">
                    repository</a>.
                </div>
            """
            ),
            self.pseudo_group,
        ]
        self.rendered = True
