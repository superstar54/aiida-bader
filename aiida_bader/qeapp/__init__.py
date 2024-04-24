from aiidalab_qe.common.panel import OutlinePanel
from aiidalab_qe.common.widgets import (
    QEAppComputationalResourcesWidget as ComputationalResourcesWidget,
)

from .result import Result
from .workchain import workchain_and_builder


class BaderOutline(OutlinePanel):
    title = "Bader charge analysis"
    help = """"""


pp_code = ComputationalResourcesWidget(
    description="pp.x",
    default_calc_job_plugin="quantumespresso.pp",
)

bader_code = ComputationalResourcesWidget(
    description="bader",
    default_calc_job_plugin="bader",
)


bader = {
    "outline": BaderOutline,
    "code": {"pp": pp_code, "bader": bader_code},
    "result": Result,
    "workchain": workchain_and_builder,
}
