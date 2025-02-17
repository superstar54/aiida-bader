"""Panel for bader plugin."""
import threading
import time
import ipywidgets as ipw
from aiidalab_qe.common.panel import ConfigurationSettingsPanel
from .model import ConfigurationSettingsModel
from aiidalab_qe.common.infobox import InAppGuide
from aiida_bader.utils import pseudo_group_exists, install_pseudos

PSEUDO_PSL_URL = "https://pseudopotentials.quantum-espresso.org/legacy_tables"


class ConfigurationSettingPanel(ConfigurationSettingsPanel[ConfigurationSettingsModel]):
    def __init__(self, model: ConfigurationSettingsModel, **kwargs):
        super().__init__(model, **kwargs)

        self._model.observe(
            self._on_pseudo_group_change,
            "pseudo_group",
        )

    def _check_and_download_pseudo_group(self):
        """Checks if the selected pseudo group exists and starts downloading if missing."""
        group_label = self._model.pseudo_group

        if not pseudo_group_exists(group_label):
            self.pseudo_status.value = (
                f'<div style="color: red;"><strong>Warning:</strong> '
                f'Pseudopotential group "{group_label}" is missing. Downloading now...</div>'
            )
            thread = threading.Thread(
                target=self._install_pseudo_in_background, args=(group_label,)
            )
            thread.start()
        else:
            self.pseudo_status.value = f'<div style="color: green;">Pseudopotential group "{group_label}" is available.</div>'

    def _install_pseudo_in_background(self, group_label):
        """Downloads and installs the missing pseudopotential group in a background thread."""
        install_pseudos(group_label)

        if pseudo_group_exists(group_label):
            self.pseudo_status.value = f'<div style="color: green;">Pseudopotential group "{group_label}" successfully installed.</div>'
        else:
            self.pseudo_status.value = (
                f'<div style="color: red;"><strong>Error:</strong> Failed to install "{group_label}". '
                f"Please check your internet connection and try again.</div>"
            )

    def render(self):
        if self.rendered:
            return

        # Error & warning messages
        self.error_message = ipw.HTML()
        self.warning_message = ipw.HTML()

        # Status message for pseudo group download
        self.pseudo_status = ipw.HTML()

        # Dropdown for selecting pseudo group
        self.pseudo_group = ipw.Dropdown(
            description="Group:",
            style={"description_width": "initial"},
        )
        ipw.dlink((self._model, "pseudo_group_options"), (self.pseudo_group, "options"))
        ipw.link((self._model, "pseudo_group"), (self.pseudo_group, "value"))

        # Check if the pseudo group exists, and trigger download if needed
        self._check_and_download_pseudo_group()

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
                <div style="line-height: 1.5; margin-bottom: 12px;">
                    <strong>Note:</strong> PAW pseudopotentials should be used for charge density calculations.
                    Please select a <span title="Choose a PAW pseudopotential group to ensure accurate calculations.">
                    PAW pseudopotential group</span> accordingly. <br>
                    The pseudopotentials are available in this
                    <a href="{PSEUDO_PSL_URL}" target="_blank" rel="noopener noreferrer">
                    Quantum ESPRESSO repository</a>.
                </div>
                """
            ),
            self.pseudo_status,  # Status message for pseudo group availability
            self.pseudo_group,
        ]
        self.rendered = True

    def _on_pseudo_group_change(self, change):
        """Callback when the pseudo group is changed."""
        self._check_and_download_pseudo_group()
