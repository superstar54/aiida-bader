"""
BaderResultsModel: Handles fetching and storing Bader charge results.
"""
from aiidalab_qe.common.panel import ResultsModel
import traitlets as tl
from aiida import orm
import time


class BaderResultsModel(ResultsModel):
    """
    Model responsible for fetching Bader-related outputs and storing them.
    """

    title = "Bader Charge"
    # (Optional) 'identifier' is used if you want to fetch processes by label.
    identifier = "bader"

    structure = tl.Instance(orm.StructureData, allow_none=True)
    site_kinds = tl.List(allow_none=True)
    bader_charges = tl.List(allow_none=True)

    _this_process_label = "QeBaderWorkChain"

    def fetch_result(self):
        """
        Fetch data from the Bader calculation workchain outputs
        and store them into the model's traitlets.
        """
        tstart = time.time()

        # 1. Obtain the root process node from the parent class. You can also
        #    override `_this_process_label` in your class if you want to
        #    automatically look up a specific label.
        root = self.fetch_process_node()

        # 2. Extract the structure and Bader charges from the outputs.
        #    Adjust attribute names as needed if your node structure is different.
        self.structure = root.inputs.bader.structure
        bader_charge_array = root.outputs.bader.bader.bader_charge.get_array("charge")

        # 3. Store relevant info in traitlets.
        self.bader_charges = [round(c, 2) for c in bader_charge_array]
        self.site_kinds = [site.kind_name for site in self.structure.sites]

        print(
            f"[BaderResultsModel] fetch_result took {time.time() - tstart:.2f} seconds"
        )
