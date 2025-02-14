"""Panel for bader plugin."""

from aiidalab_qe.common.panel import ConfigurationSettingsPanel
import ipywidgets as ipw
from .model import ConfigurationSettingsModel
from aiidalab_qe.common.infobox import InAppGuide


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

        self.children = [
            self.error_message,
            self.warning_message,
            InAppGuide(identifier="bader-settings"),
        ]
        self.rendered = True
