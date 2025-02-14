from aiidalab_qe.common.panel import PluginOutline

from .resources import ResourceSettingsModel, ResourceSettingsPanel
from .workchain import workchain_and_builder
from .result import BaderResultsPanel, BaderResultsModel
from .setting import ConfigurationSettingPanel
from .model import ConfigurationSettingsModel


class PluginOutline(PluginOutline):
    title = "Bader charge analysis"


bader = {
    "outline": PluginOutline,
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
}
