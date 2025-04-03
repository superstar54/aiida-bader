from aiidalab_qe.common.panel import PluginOutline

from .resources import ResourceSettingsModel, ResourceSettingsPanel
from .workchain import workchain_and_builder
from .result import BaderResultsPanel, BaderResultsModel
from .setting import ConfigurationSettingPanel
from .model import ConfigurationSettingsModel
from .structure_examples import structure_examples
from pathlib import Path


class PluginOutline(PluginOutline):
    title = "Bader charge analysis"


bader = {
    "outline": PluginOutline,
    "structure_examples": structure_examples,
    "configuration": {
        "panel": ConfigurationSettingPanel,
        "model": ConfigurationSettingsModel,
    },
    "resources": {
        "panel": ResourceSettingsPanel,
        "model": ResourceSettingsModel,
    },
    "workchain": workchain_and_builder,
    "result": {
        "panel": BaderResultsPanel,
        "model": BaderResultsModel,
    },
    "guides": {
        "title": "Bader charge analysis",
        "path": Path(__file__).resolve().parent / "guides",
    },
    "metadata": {
        "process_labels": {
            "QeBaderWorkChain": "Bader charge workflow",
            "PpCalculation": "Compute charge density",
            "BaderCalculation": "Compute Bader charge",
        }
    },
}
