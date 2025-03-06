"""
BaderResultsModel: Handles fetching and storing Bader charge results.
"""
from aiidalab_qe.common.panel import ResultsModel
import traitlets as tl
from aiida import orm
import time


class BaderResultsModel(ResultsModel):

    title = "Bader Charge"
    identifier = "bader"

    structure = tl.Instance(orm.StructureData, allow_none=True)
    bader_charges = tl.List(allow_none=True)
    z_valencces = tl.Dict(allow_none=True)

    _this_process_label = "QeBaderWorkChain"

    def fetch_result(self):
        """
        Fetch data from the Bader calculation workchain outputs
        and store them into the model's traitlets.
        """
        root = self.fetch_process_node()

        self.structure = root.inputs.bader.structure
        for key, pseudo in root.inputs.bader.scf.pw.pseudos.items():
            if getattr(pseudo, "z_valence", False):
                self.z_valencces[key] = getattr(pseudo, "z_valence")
        bader_charge_array = root.outputs.bader.bader.bader_charge.get_array("charge")

        self.bader_charges = [round(c, 2) for c in bader_charge_array]
